from __future__ import absolute_import

import os
import sys

from logging import Logger, StreamHandler

from .color import SUPPORTS_COLOR
from .formatter import THEME, MAX_LENGTH, PIPE_CHAR, CAP_CHAR, ExceptionFormatter


def _stream_supports_color(stream):
    """Check whether a given stream supports color output.

    Color is enabled when either:
    - ``FORCE_COLOR=1`` is set in the environment (explicit override), or
    - the global ``SUPPORTS_COLOR`` flag is True AND the stream is a TTY.

    When the stream is not a TTY (e.g. a file or a pipe), colors are
    disabled by default to avoid escape sequences leaking into log files.
    """
    if os.getenv('FORCE_COLOR', None) == '1':
        return True

    if not SUPPORTS_COLOR:
        return False

    is_tty = False
    try:
        is_tty = bool(getattr(stream, 'isatty', lambda: False)())
    except Exception:
        is_tty = False

    return is_tty


def _make_logging_format_exception(stream):
    """Create a formatException function that respects the stream's TTY status."""
    def logging_format_exception(exc_info):
        colored = _stream_supports_color(stream)
        formatter = ExceptionFormatter(
            colored=colored, theme=THEME, max_length=MAX_LENGTH,
            pipe_char=PIPE_CHAR, cap_char=CAP_CHAR,
        )
        return u''.join(formatter.format_exception(*exc_info))
    return logging_format_exception


def patch():
    import logging

    if hasattr(logging, '_defaultFormatter'):
        # The _defaultFormatter is used as a fallback; use stderr to decide
        # whether color is appropriate.
        logging._defaultFormatter.formatException = _make_logging_format_exception(sys.stderr)

    patchables = [handler() for handler in logging._handlerList if isinstance(handler(), StreamHandler)]
    patchables = [handler for handler in patchables if handler.stream == sys.stderr]
    patchables = [handler for handler in patchables if handler.formatter is not None]
    for handler in patchables:
        handler.formatter.formatException = _make_logging_format_exception(handler.stream)


class BetExcLogger(Logger):
    def __init__(self, *args, **kwargs):
        super(BetExcLogger, self).__init__(*args, **kwargs)
        patch()
