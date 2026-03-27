from __future__ import absolute_import

import sys

from logging import Logger, StreamHandler


def patch():
    import logging
    from . import format_exception

    # Use colored=False for logging output. Python's logging module caches
    # formatted exception text in record.exc_text, which is shared across all
    # handlers. If a StreamHandler formats with ANSI color codes, that cached
    # text leaks into FileHandlers and other non-terminal destinations.
    # Unhandled exceptions still render with colors via sys.excepthook.
    def logging_format_exception(exc_info):
        return u''.join(format_exception(*exc_info, colored=False))

    if hasattr(logging, '_defaultFormatter'):
        logging._defaultFormatter.formatException = logging_format_exception

    for handler_ref in logging._handlerList:
        handler = handler_ref()
        if handler is None:
            continue
        if not isinstance(handler, StreamHandler):
            continue
        if handler.stream != sys.stderr:
            continue
        if handler.formatter is None:
            continue
        handler.formatter.formatException = logging_format_exception


class BetExcLogger(Logger):
    def __init__(self, *args, **kwargs):
        super(BetExcLogger, self).__init__(*args, **kwargs)
        patch()
