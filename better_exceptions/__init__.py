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

from .formatter import THEME, MAX_LENGTH, ExceptionFormatter
from .color import SUPPORTS_COLOR, STREAM
from .log import BetExcLogger, patch as patch_logging
from .repl import interact, get_repl


__version__ = '0.2.2'


ENCODING = STREAM.encoding
THEME = THEME.copy()  # Users customizing the theme should not impact core


def format_exception(exc, value, tb):
    # Rebuild each time to take into account any changes made by the user to the global parameters
    formatter = ExceptionFormatter(
        colored=SUPPORTS_COLOR, theme=THEME, max_length=MAX_LENGTH, encoding=ENCODING
    )
    return list(formatter.format_exception(exc, value, tb))


def excepthook(exc, value, tb):
    formatted = ''.join(format_exception(exc, value, tb))
    STREAM.write(formatted)


def hook():
    sys.excepthook = excepthook

    logging.setLoggerClass(BetExcLogger)
    patch_logging()

    if hasattr(sys, 'ps1'):
        print('WARNING: better_exceptions will only inspect code from the command line\n'
              '         when using: `python -m better_exceptions\'. Otherwise, only code\n'
              '         loaded from files will be inspected!', file=sys.stderr)
