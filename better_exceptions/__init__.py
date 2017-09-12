"""Beautiful and helpful exceptions

Just `import better_exceptions` somewhere. It handles the rest.


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

from .core import color, context, encoding, log, repl
from .core import SUPPORTS_COLOR, THEME, MAX_LENGTH, PIPE_CHAR, CAP_CHAR
from .core import __version__, isast, write_stream, ExceptionFormatter
from .core.log import BetExcLogger, patch as patch_logging
from .core.repl import interact, get_repl


THEME = THEME.copy()  # Users customizing the theme should not impact core


def format_exception(exc, value, tb):
    # Rebuild each time to take into account any changes made by the user to the global parameters
    formatter = ExceptionFormatter(colored=SUPPORTS_COLOR, theme=THEME, max_length=MAX_LENGTH,
                                   pipe_char=PIPE_CHAR, cap_char=CAP_CHAR)
    return formatter.format_exception(exc, value, tb)


def excepthook(exc, value, tb):
    formatted = format_exception(exc, value, tb)
    write_stream(formatted)


sys.excepthook = excepthook


logging.setLoggerClass(BetExcLogger)
patch_logging()


if hasattr(sys, 'ps1'):
    print('WARNING: better_exceptions will only inspect code from the command line\n'
          '         when using: `python -m better_exceptions\'. Otherwise, only code\n'
          '         loaded from files will be inspected!', file=sys.stderr)
