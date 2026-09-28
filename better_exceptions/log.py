from __future__ import absolute_import

import logging

from logging import Logger


def _uncolored_format_exception(exc_info):
    """Format an exception for logging without ANSI color codes.

    Terminal ``excepthook`` output remains colored separately. Logged
    exceptions are often viewed in editors/files where escape codes are noise.
    """
    from .formatter import CAP_CHAR, ExceptionFormatter, MAX_LENGTH, PIPE_CHAR, THEME

    formatter = ExceptionFormatter(
        colored=False,
        theme=THEME,
        max_length=MAX_LENGTH,
        pipe_char=PIPE_CHAR,
        cap_char=CAP_CHAR,
    )
    return u''.join(formatter.format_exception(*exc_info))


def patch():
    logging_format_exception = _uncolored_format_exception

    if hasattr(logging, '_defaultFormatter'):
        logging._defaultFormatter.format_exception = logging_format_exception

    for handler_ref in list(getattr(logging, '_handlerList', [])):
        handler = handler_ref() if callable(handler_ref) else None
        if handler is None or getattr(handler, 'formatter', None) is None:
            continue
        # Always uncolor logged exceptions (FileHandler, StreamHandler, etc.).
        # Interactive terminal coloring is handled by sys.excepthook, not logging.
        handler.formatter.formatException = logging_format_exception


class BetExcLogger(Logger):
    def __init__(self, *args, **kwargs):
        super(BetExcLogger, self).__init__(*args, **kwargs)
        patch()
