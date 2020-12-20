from __future__ import absolute_import

import ast
import inspect
import keyword
import linecache
import os
import re
import sys
import traceback

from .color import STREAM, SUPPORTS_COLOR
from .context import PY3
from .encoding import ENCODING, to_byte, to_unicode
from .repl import get_repl


PIPE_CHAR = u'\u2502'
CAP_CHAR = u'\u2514'

try:
    PIPE_CHAR.encode(ENCODING)
except UnicodeEncodeError:
    PIPE_CHAR = '|'
    CAP_CHAR = '->'

THEME = {
    'comment': lambda s: '\x1b[2;37m{}\x1b[m'.format(s),
    'keyword': lambda s: '\x1b[33;1m{}\x1b[m'.format(s),
    'builtin': lambda s: '\x1b[35;1m{}\x1b[m'.format(s),
    'literal': lambda s: '\x1b[31m{}\x1b[m'.format(s),
    'inspect': lambda s: u'\x1b[36m{}\x1b[m'.format(s),
}

MAX_LENGTH = 128


def isast(v):
    return inspect.isclass(v) and issubclass(v, ast.AST)


class ExceptionFormatter(object):

    COMMENT_REGXP = re.compile(r'((?:(?:"(?:[^\\"]|(\\\\)*\\")*")|(?:\'(?:[^\\\']|(\\\\)*\\\')*\')|[^#])*)(#.*)$')
    CMDLINE_REGXP = re.compile(r'(?:[^\t ]*([\'"])(?:\\.|.)*(?:\1))[^\t ]*|([^\t ]+)')

    AST_ELEMENTS = {
        'builtins': __builtins__.keys() if type(__builtins__) is dict else dir(__builtins__),
        'keywords': [getattr(ast, cls) for cls in dir(ast) if keyword.iskeyword(cls.lower()) and isast(getattr(ast, cls))],
    }

    def __init__(self, colored=SUPPORTS_COLOR, theme=THEME, max_length=MAX_LENGTH,
                       pipe_char=PIPE_CHAR, cap_char=CAP_CHAR):
        self._colored = colored
        self._theme = theme
        self._max_length = max_length
        self._pipe_char = pipe_char
        self._cap_char = cap_char

    def colorize_comment(self, source):
        match = self.COMMENT_REGXP.match(source)
        if match:
            source = '{}{}'.format(match.group(1), self._theme['comment'](match.group(4)))
        return source

    def colorize_tree(self, tree, source):
        if not self._colored:
            # quick fail
            return source

        chunks = []

        offset = 0
        nodes = [n for n in ast.walk(tree)]

        def append(offset, node, s, theme):
            begin_col = node.col_offset
            src_chunk = source[offset:begin_col]
            chunks.append(src_chunk)
            chunks.append(self._theme[theme](s))
            return begin_col + len(s)

        displayed_nodes = []

        for node in nodes:
            nodecls = node.__class__
            nodename = nodecls.__name__

            if 'col_offset' not in dir(node):
                continue

            if nodecls in self.AST_ELEMENTS['keywords']:
                displayed_nodes.append((node, nodename.lower(), 'keyword'))

            if nodecls == ast.Name and node.id in self.AST_ELEMENTS['builtins']:
                displayed_nodes.append((node, node.id, 'builtin'))

            if nodecls == ast.Str:
                displayed_nodes.append((node, "'{}'".format(node.s), 'literal'))

            if nodecls == ast.Num:
                displayed_nodes.append((node, str(node.n), 'literal'))

        displayed_nodes.sort(key=lambda elem: elem[0].col_offset)

        for dn in displayed_nodes:
            offset = append(offset, *dn)

        chunks.append(source[offset:])
        return self.colorize_comment(''.join(chunks))

    def get_relevant_names(self, source, tree):
        return [node for node in ast.walk(tree) if isinstance(node, ast.Name)]

    def format_value(self, v):
        try:
            v = repr(v)
        except KeyboardInterrupt:
            raise
        except BaseException:
            v = u'<unprintable %s object>' % type(v).__name__

        max_length = self._max_length
        if max_length is not None and len(v) > max_length:
            v = v[:max_length] + '...'
        return v

    def get_relevant_values(self, source, frame, tree):
        names = self.get_relevant_names(source, tree)
        values = []

        for name in names:
            text = name.id
            col = name.col_offset
            if text in frame.f_locals:
                val = frame.f_locals.get(text, None)
                values.append((text, col, self.format_value(val)))
            elif text in frame.f_globals:
                val = frame.f_globals.get(text, None)
                values.append((text, col, self.format_value(val)))

        values.sort(key=lambda e: e[1])

        return values

    def split_cmdline(self, cmdline):
        return [m.group(0) for m in self.CMDLINE_REGXP.finditer(cmdline)]

    def get_string_source(self):
        import os
        import platform

        # import pdb; pdb.set_trace()

        cmdline = None
        if platform.system() == 'Windows':
            # TODO use winapi to obtain the command line
            return ''
        elif platform.system() == 'Linux':
            # TODO try to use proc
            pass

        if cmdline is None and os.name == 'posix':
            from shutil import which

            if which('ps'):
                from subprocess import CalledProcessError, check_output as spawn

                try:
                    cmdline = spawn(['ps', '-ww', '-p', str(os.getpid()), '-o', 'command='])
                except CalledProcessError:
                    return ''
            else:
                return ''
        else:
            # current system doesn't have a way to get the command line
            return ''

        cmdline = cmdline.decode('utf-8').strip()
        cmdline = self.split_cmdline(cmdline)

        extra_args = sys.argv[1:]
        if len(extra_args) > 0:
            if cmdline[-len(extra_args):] != extra_args:
                # we can't rely on the output to be correct; fail!
                return ''

            cmdline = cmdline[1:-len(extra_args)]

        skip = 0
        for i in range(len(cmdline)):
            a = cmdline[i].strip()
            if not a.startswith('-c'):
                skip += 1
            else:
                a = a[2:].strip()
                if len(a) > 0:
                    cmdline[i] = a
                else:
                    skip += 1
                break

        cmdline = cmdline[skip:]
        source = ' '.join(cmdline)

        return source

    def get_traceback_information(self, tb):
        frame_info = inspect.getframeinfo(tb)
        filename = frame_info.filename
        lineno = frame_info.lineno
        function = frame_info.function

        repl = get_repl()
        if repl is not None and filename in repl.entries:
            _, filename, source = repl.entries[filename]
            source = source.replace('\r\n', '\n').split('\n')[lineno - 1]
        elif filename == '<string>':
            source = self.get_string_source()
        else:
            source = linecache.getline(filename, lineno)

        source = source.strip()

        try:
            tree = ast.parse(source, mode='exec')
        except SyntaxError:
            return filename, lineno, function, source, source, []

        relevant_values = self.get_relevant_values(source, tb.tb_frame, tree)
        color_source = self.colorize_tree(tree, source)

        return filename, lineno, function, source, color_source, relevant_values


    def format_traceback_frame(self, tb):
        filename, lineno, function, source, color_source, relevant_values = self.get_traceback_information(tb)

        lines = [color_source]
        for i in reversed(range(len(relevant_values))):
            _, col, val = relevant_values[i]
            pipe_cols = [pcol for _, pcol, _ in relevant_values[:i]]
            line = ''
            index = 0
            for pc in pipe_cols:
                line += (' ' * (pc - index)) + self._pipe_char
                index = pc + 1

            if not PY3 and isinstance(val, str):
                # In Python2 the Non-ASCII value will be the escaped string,
                # use string-escape to decode the string to show the text in human way.
                val = to_unicode(val.decode("string-escape"))

            line += u'{}{} {}'.format((' ' * (col - index)), self._cap_char, val)
            lines.append(self._theme['inspect'](line) if self._colored else line)
        formatted = u'\n    '.join([to_unicode(x) for x in lines])

        return (filename, lineno, function, formatted), color_source


    def format_traceback(self, tb=None):
        omit_last = False
        if not tb:
            try:
                raise Exception()
            except:
                omit_last = True
                _, _, tb = sys.exc_info()
                assert tb is not None

        frames = []
        final_source = ''
        while tb:
            if omit_last and not tb.tb_next:
                break

            formatted, colored = self.format_traceback_frame(tb)

            # special case to ignore runcode() here.
            if not (os.path.basename(formatted[0]) == 'code.py' and formatted[2] == 'runcode'):
                final_source = colored
                frames.append(formatted)

            tb = tb.tb_next

        lines = traceback.format_list(frames)

        return ''.join(lines), final_source

    def _format_exception(self, value, tb, seen=None):
        # Implemented from built-in traceback module:
        # https://github.com/python/cpython/blob/a5b76167dedf4d15211a216c3ca7b98e3cec33b8/Lib/traceback.py#L468

        exc_type, exc_value, exc_traceback = type(value), value, tb

        if seen is None:
            seen = set()

        seen.add(id(exc_value))

        if exc_value and PY3:
            if exc_value.__cause__ is not None and id(exc_value.__cause__) not in seen:
                for text in self._format_exception(exc_value.__cause__,exc_value.__cause__.__traceback__, seen=seen):
                    yield text
                yield u"\nThe above exception was the direct cause of the following exception:\n\n"
            elif exc_value.__context__ is not None and id(exc_value.__context__) not in seen and not exc_value.__suppress_context__:
                for text in self._format_exception(exc_value.__context__, exc_value.__context__.__traceback__, seen=seen):
                    yield text
                yield u"\nDuring handling of the above exception, another exception occurred:\n\n"

        if exc_traceback is not None:
            yield u'Traceback (most recent call last):\n'

        formatted, colored_source = self.format_traceback(exc_traceback)

        yield formatted

        if not str(value) and exc_type is AssertionError:
            value.args = (colored_source,)
        title = traceback.format_exception_only(exc_type, value)

        yield u''.join(title).strip() + u'\n'

    def format_exception(self, exc, value, tb):
        for line in self._format_exception(value, tb):
            yield line
