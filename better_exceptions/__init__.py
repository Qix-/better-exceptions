"""Beautiful and helpful exceptions

Just set your `BETTER_EXCEPTIONS` environment variable. It handles the rest.


   Name: better_exceptions
 Author: Josh Junon
  Email: josh@junon.me
    URL: github.com/qix-/better-exceptions
License: Copyright (c) 2017 Josh Junon, licensed under the MIT license
"""

from __future__ import absolute_import
from __future__ import print_function

import logging
import sys

from .formatter import THEME, MAX_LENGTH, PIPE_CHAR, CAP_CHAR, ExceptionFormatter
from .encoding import to_byte
from .context import PY3
from .color import SUPPORTS_COLOR, SHOULD_ENCODE, STREAM
from .log import BetExcLogger, patch as patch_logging
from .repl import interact, get_repl


__version__ = '0.3.3'


THEME = THEME.copy()  # Users customizing the theme should not impact core


def write_stream(data, stream=STREAM):
    if SHOULD_ENCODE:
        data = to_byte(data)

        if PY3:
            stream.buffer.write(data)
        else:
            stream.write(data)
    else:
        stream.write(data)


def format_exception(exc, value, tb):
    # Rebuild each time to take into account any changes made by the user to the global parameters
    formatter = ExceptionFormatter(colored=SUPPORTS_COLOR, theme=THEME, max_length=MAX_LENGTH,
                                   pipe_char=PIPE_CHAR, cap_char=CAP_CHAR)
    return list(formatter.format_exception(exc, value, tb))


def excepthook(exc, value, tb):
    formatted = u''.join(format_exception(exc, value, tb))
    write_stream(formatted, STREAM)


def hook():
    sys.excepthook = excepthook

    logging.setLoggerClass(BetExcLogger)
    patch_logging()

    if hasattr(sys, 'ps1'):
        print('WARNING: better_exceptions will only inspect code from the command line\n'
              '         when using: `python -m better_exceptions\'. Otherwise, only code\n'
              '         loaded from files will be inspected!', file=sys.stderr)
