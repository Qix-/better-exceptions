from __future__ import absolute_import

import sys

from copy import copy
from logging import FileHandler, Logger, StreamHandler


def patch():
    import logging
    from . import format_exception

    logging_format_exception = lambda exc_info: u''.join(format_exception(*exc_info))

    def patch_formatter(formatter):
        if getattr(formatter, '_better_exceptions_patched', False):
            return

        original_format = formatter.format

        def logging_format(record):
            exc_text = record.exc_text
            record.exc_text = None
            try:
                return original_format(record)
            finally:
                record.exc_text = exc_text

        formatter.formatException = logging_format_exception
        formatter.format = logging_format
        formatter._better_exceptions_patched = True

    if hasattr(logging, '_defaultFormatter'):
        logging._defaultFormatter.format_exception = logging_format_exception

    for handler_ref in logging._handlerList:
        handler = handler_ref()
        if handler is None:
            continue

        if not isinstance(handler, StreamHandler) or isinstance(handler, FileHandler):
            continue

        if handler.stream != sys.stderr or handler.formatter is None:
            continue

        formatter = handler.formatter
        for other_handler_ref in logging._handlerList:
            other_handler = other_handler_ref()
            if other_handler is not None and other_handler is not handler and other_handler.formatter is formatter:
                formatter = copy(formatter)
                handler.setFormatter(formatter)
                break

        patch_formatter(formatter)


class BetExcLogger(Logger):
    def __init__(self, *args, **kwargs):
        super(BetExcLogger, self).__init__(*args, **kwargs)
        patch()
