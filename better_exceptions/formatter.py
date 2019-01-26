from __future__ import absolute_import

import inspect
import keyword
import linecache
import os
import re
import sys
import tokenize
import traceback

from .color import STREAM, SUPPORTS_COLOR
from .encoding import ENCODING, to_byte, to_unicode
from .highlighter import STYLE, Highlighter
from .repl import get_repl


PIPE_CHAR = '\u2502'
CAP_CHAR = '\u2514'

try:
    PIPE_CHAR.encode(ENCODING)
except UnicodeEncodeError:
    PIPE_CHAR = '|'
    CAP_CHAR = '->'

THEME = {
    'inspect': '\x1b[36m{}\x1b[m',
}

MAX_LENGTH = 128


class ExceptionFormatter(object):

    CMDLINE_REGXP = re.compile(r'(?:[^\t ]*([\'"])(?:\\.|.)*(?:\1))[^\t ]*|([^\t ]+)')

    def __init__(self, colored=SUPPORTS_COLOR, style=STYLE, theme=THEME, max_length=MAX_LENGTH,
                       pipe_char=PIPE_CHAR, cap_char=CAP_CHAR):
        self._colored = colored
        self._theme = theme
        self._max_length = max_length
        self._pipe_char = pipe_char
        self._cap_char = cap_char
        self._highlighter = Highlighter(style)

    def format_value(self, v):
        try:
            v = repr(v)
        except Exception:
            v = '<unprintable %s object>' % type(v).__name__

        max_length = self._max_length
        if max_length is not None and len(v) > max_length:
            v = v[:max_length] + '...'
        return v

    def get_relevant_values(self, source, frame):
        values = []
        value = None
        is_attribute = False
        is_valid_value = False

        for token in self._highlighter.tokenize(source):
            type_, string, (_, col), *_ = token

            if type_ == tokenize.NAME and not keyword.iskeyword(string):
                if not is_attribute:
                    for variables in (frame.f_locals, frame.f_globals):
                        try:
                            value = variables[string]
                        except KeyError:
                            continue
                        else:
                            is_valid_value = True
                            values.append((col, self.format_value(value)))
                            break
                elif is_valid_value:
                    try:
                        value = inspect.getattr_static(value, string)
                    except AttributeError:
                        is_valid_value = False
                    else:
                        values.append((col, self.format_value(value)))
            elif type_ == tokenize.OP and string == ".":
                is_attribute = True
            else:
                is_attribute = False
                is_valid_value = False

        values.sort()

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
            from subprocess import CalledProcessError, check_output as spawn

            try:
                cmdline = spawn(['ps', '-ww', '-p', str(os.getpid()), '-o', 'command='])
            except CalledProcessError:
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

        relevant_values = self.get_relevant_values(source, tb.tb_frame)

        if self._colored:
            color_source = self._highlighter.highlight(source)
        else:
            color_source = source

        return filename, lineno, function, source, color_source, relevant_values


    def format_traceback_frame(self, tb):
        filename, lineno, function, source, color_source, relevant_values = self.get_traceback_information(tb)

        lines = [color_source]
        for i in reversed(range(len(relevant_values))):
            col, val = relevant_values[i]
            pipe_cols = [pcol for pcol, _ in relevant_values[:i]]
            pre_line = ''
            index = 0

            for pc in pipe_cols:
                pre_line += (' ' * (pc - index)) + self._pipe_char
                index = pc + 1

            pre_line += ' ' * (col - index)
            val_lines = val.split('\n')

            for n, val_line in enumerate(val_lines):
                if n == 0:
                    line = pre_line + self._cap_char + ' ' + val_line
                else:
                    line = pre_line + ' ' * (len(self._cap_char) + 1) + val_line

                lines.append(self._theme['inspect'].format(line) if self._colored else line)

        formatted = '\n    '.join([to_unicode(x) for x in lines])

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

        if exc_value:
            if exc_value.__cause__ is not None and id(exc_value.__cause__) not in seen:
                for text in self._format_exception(exc_value.__cause__,exc_value.__cause__.__traceback__, seen=seen):
                    yield text
                yield "\nThe above exception was the direct cause of the following exception:\n\n"
            elif exc_value.__context__ is not None and id(exc_value.__context__) not in seen and not exc_value.__suppress_context__:
                for text in self._format_exception(exc_value.__context__, exc_value.__context__.__traceback__, seen=seen):
                    yield text
                yield "\nDuring handling of the above exception, another exception occurred:\n\n"

        if exc_traceback is not None:
            yield 'Traceback (most recent call last):\n'

        formatted, colored_source = self.format_traceback(exc_traceback)

        yield formatted

        if not str(value) and exc_type is AssertionError:
            value.args = (colored_source,)
        title = traceback.format_exception_only(exc_type, value)

        yield ''.join(title).strip() + '\n'

    def format_exception(self, exc, value, tb):
        for line in self._format_exception(value, tb):
            yield line
