from __future__ import absolute_import

import sys

from logging import Logger, StreamHandler


def patch():
    import logging
    from . import format_exception

    logging_format_exception = lambda exc_info: u''.join(format_exception(*exc_info))

    if hasattr(logging, '_defaultFormatter'):
        logging._defaultFormatter.format_exception = logging_format_exception

    patchables = [handler() for handler in logging._handlerList if isinstance(handler(), StreamHandler)]
    patchables = [handler for handler in patchables if handler.stream == sys.stderr]
    patchables = [handler for handler in patchables if handler.formatter is not None]
    for handler in patchables:
        handler.formatter.formatException = logging_format_exception


class BetExcLogger(Logger):
    def __init__(self, *args, **kwargs):
        super(BetExcLogger, self).__init__(*args, **kwargs)
        patch()
