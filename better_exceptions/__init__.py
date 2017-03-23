"""Beautiful and helpful exceptions

Just `import better_exceptions` somewhere. It handles the rest.


   Name: better_exceptions
 Author: Josh Junon
  Email: josh@junon.me
    URL: github.com/qix-/better-exceptions
License: Copyright (c) 2017 Josh Junon, licensed under the MIT license
"""

from __future__ import absolute_import

import ast
import inspect
import keyword
import linecache
import locale
import os
import re
import sys
import traceback

from better_exceptions.color import STREAM, SUPPORTS_COLOR


def isast(v):
    return inspect.isclass(v) and issubclass(v, ast.AST)


ENCODING = locale.getpreferredencoding()

PIPE_CHAR = u'\u2502'
CAP_CHAR = u'\u2514'

try:
    PIPE_CHAR.encode(ENCODING)
except UnicodeEncodeError:
    PIPE_CHAR = '|'
    CAP_CHAR = '->'

COMMENT_REGXP = re.compile(r'((?:(?:"(?:[^\\"]|(\\\\)*\\")*")|(?:\'(?:[^\\"]|(\\\\)*\\\')*\')|[^#])*)(#.*)$')

AST_ELEMENTS = {
    'builtins': __builtins__.keys(),
    'keywords': [getattr(ast, cls) for cls in dir(ast) if keyword.iskeyword(cls.lower()) and isast(getattr(ast, cls))],
}

THEME = {
    'comment': lambda s: '\x1b[2;37m{}\x1b[m'.format(s),
    'keyword': lambda s: '\x1b[33;1m{}\x1b[m'.format(s),
    'builtin': lambda s: '\x1b[35;1m{}\x1b[m'.format(s),
    'literal': lambda s: '\x1b[31m{}\x1b[m'.format(s),
    'inspect': lambda s: s if not SUPPORTS_COLOR else u'\x1b[36m{}\x1b[m'.format(s),
}

MAX_LENGTH = 128


def colorize_comment(source):
    match = COMMENT_REGXP.match(source)
    if match:
        source = '{}{}'.format(match.group(1), THEME['comment'](match.group(4)))
    return source


def colorize_tree(tree, source):
    if not SUPPORTS_COLOR:
        # quick fail
        return source

    chunks = []

    offset = 0
    nodes = [n for n in ast.walk(tree)]
    nnodes = len(nodes)

    def append(offset, node, s, theme):
        begin_col = node.col_offset
        chunks.append(source[offset:begin_col])
        chunks.append(THEME[theme](s))
        return begin_col + len(s)

    for i in range(nnodes):
        node = nodes[i]
        nodecls = node.__class__
        nodename = nodecls.__name__

        if 'col_offset' not in dir(node):
            # this would probably benefit from using the `parser` module in the future...
            continue

        if nodecls in AST_ELEMENTS['keywords']:
            offset = append(offset, node, nodename.lower(), 'keyword')

        if nodecls == ast.Name and node.id in AST_ELEMENTS['builtins']:
            offset = append(offset, node, node.id, 'builtin')

        if nodecls == ast.Str:
            offset = append(offset, node, "'{}'".format(node.s), 'literal')

        if nodecls == ast.Num:
            offset = append(offset, node, str(node.n), 'literal')

    chunks.append(source[offset:])
    return colorize_comment(''.join(chunks))


def get_relevant_names(source, tree):
    return [node for node in ast.walk(tree) if isinstance(node, ast.Name)]


def format_value(v):
    v = repr(v)
    if MAX_LENGTH is not None and len(v) > MAX_LENGTH:
        v = v[:MAX_LENGTH] + '...'
    return v


def get_relevant_values(source, frame, tree):
    names = get_relevant_names(source, tree)
    values = []

    for name in names:
        text = name.id
        col = name.col_offset
        if text in frame.f_locals:
            val = frame.f_locals.get(text, None)
            values.append((text, col, format_value(val)))
        elif text in frame.f_globals:
            val = frame.f_globals.get(text, None)
            values.append((text, col, format_value(val)))

    values.sort(key=lambda e: e[1])

    return values


def get_traceback_information(tb):
    frame_info = inspect.getframeinfo(tb)
    filename = frame_info.filename
    lineno = frame_info.lineno
    function = frame_info.function
    source = linecache.getline(filename, lineno).strip()

    try:
        tree = ast.parse(source, mode='exec')
    except SyntaxError:
        return filename, lineno, function, source, source, []

    relevant_values = get_relevant_values(source, tb.tb_frame, tree)
    color_source = colorize_tree(tree, source)

    return filename, lineno, function, source, color_source, relevant_values


def format_traceback_frame(tb):
    filename, lineno, function, source, color_source, relevant_values = get_traceback_information(tb)

    lines = [color_source]
    for i in reversed(range(len(relevant_values))):
        _, col, val = relevant_values[i]
        pipe_cols = [pcol for _, pcol, _ in relevant_values[:i]]
        line = ''
        index = 0
        for pc in pipe_cols:
            line += (' ' * (pc - index)) + PIPE_CHAR
            index = pc + 1
        line += u'{}{} {}'.format((' ' * (col - index)), CAP_CHAR, val)
        lines.append(THEME['inspect'](line))

    formatted = '\n    '.join(lines)

    return (filename, lineno, function, formatted), color_source


def format_traceback(tb=None):
    if not tb:
        try:
            raise Exception()
        except:
            _, _, tb = sys.exc_info()

    frames = []
    while tb:
        formatted, colored = format_traceback_frame(tb)
        final_source = colored
        frames.append(formatted)
        tb = tb.tb_next

    lines = traceback.format_list(frames)

    return ''.join(lines), final_source


def write_stream(data):
    data = data.encode(ENCODING)

    if sys.version_info[0] < 3:
        STREAM.write(data)
    else:
        STREAM.buffer.write(data)


def excepthook(exc, value, tb):
    formatted, colored_source = format_traceback(tb)

    if not str(value) and exc is AssertionError:
        value.args = (colored_source,)
    title = traceback.format_exception_only(exc, value)

    full_trace = u'Traceback (most recent call last):\n{}{}\n'.format(formatted, title[0].strip())
    write_stream(full_trace)


sys.excepthook = excepthook
