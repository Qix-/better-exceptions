"""Beautiful and helpful exceptions

Just `import better_exceptions` somewhere. It handles the rest.


   Name: better_exceptions
 Author: Josh Junon
  Email: josh@junon.me
    URL: github.com/qix-/better-exceptions
License: Copyright (c) 2017 Josh Junon, licensed under the MIT licens
"""

from __future__ import absolute_import
from __future__ import print_function

import _ast
import ast
import inspect
import keyword
import os
import re
import sys
import traceback


def isast(v):
    return inspect.isclass(v) and issubclass(v, ast.AST)


NOCOLOR = not os.isatty(2) or os.name == 'nt' or os.getenv('TERM', '')[:5] != 'xterm'

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
    'inspect': lambda s: s if NOCOLOR else u'\x1b[36m{}\x1b[m'.format(s),
}

MAX_LENGTH = 128


def colorize_comment(source):
    match = COMMENT_REGXP.match(source)
    if match:
        source = '{}{}'.format(match.group(1), THEME['comment'](match.group(4)))
    return source


def colorize_tree(tree, source):
    if NOCOLOR:
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

    for i in xrange(nnodes):
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


def get_source_line(frame):
    line = frame.f_lineno
    try:
        filename = inspect.getsourcefile(frame)
    except TypeError:
        return None

    count = 1
    with open(frame.f_code.co_filename, 'r') as f:
        while count < line:
            next(f)
            count += 1
        return (filename, line, next(f).strip())


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
        if frame.f_locals.has_key(text):
            val = frame.f_locals.get(text, None)
            values.append((text, col, format_value(val)))
        elif frame.f_globals.has_key(text):
            val = frame.f_globals.get(text, None)
            values.append((text, col, format_value(val)))

    values.sort(key=lambda e: e[1])

    return values


def get_frame_information(frame):
    function = inspect.getframeinfo(frame)[2]
    filename, lineno, source = get_source_line(frame)
    try:
        tree = ast.parse(source, mode='exec')
    except SyntaxError:
        return filename, lineno, function, source, source, []
    mod = inspect.getmodule(frame)

    relevant_values = get_relevant_values(source, frame, tree)
    color_source = colorize_tree(tree, source)


    return filename, lineno, function, source, color_source, relevant_values


def format_frame(frame):
    filename, lineno, function, source, color_source, relevant_values = get_frame_information(frame)

    lines = [color_source]

    for i in reversed(xrange(len(relevant_values))):
        _, col, val = relevant_values[i]
        pipe_cols = [pcol for _, pcol, _ in relevant_values[:i]]
        line = ''
        index = 0
        for pc in pipe_cols:
            line += ' ' * (pc - index) + u'\u2502'
            index = pc + 1
        line += (' ' * (col - index)) + u'\u2515 ' + val
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
        formatted, colored = format_frame(tb.tb_frame)
        final_source = colored
        frames.append(formatted)
        tb = tb.tb_next

    lines = traceback.format_list(frames)

    return ''.join(lines), final_source


def excepthook(exc, value, tb):
    formatted, colored_source = format_traceback(tb)

    if not str(value) and exc is AssertionError:
        title = traceback.format_exception_only(exc, colored_source)
    else:
        title = traceback.format_exception_only(exc, value)

    full_trace = u'Traceback (most recent call last):\n{}{}'.format(formatted, title[0].strip())

    print(full_trace, file=sys.stderr)

sys.excepthook = excepthook
