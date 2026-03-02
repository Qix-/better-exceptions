from __future__ import absolute_import

import sys

from logging import Logger, StreamHandler


def patch():
    import logging
    from . import format_exception

    logging_format_exception_colored = lambda exc_info: u''.join(format_exception(*exc_info, colored=True))
    logging_format_exception_plain = lambda exc_info: u''.join(format_exception(*exc_info, colored=False))

    patchables = [handler() for handler in logging._handlerList if handler() is not None]
    patchables = [handler for handler in patchables if handler.formatter is not None]

    for handler in patchables:
        # Keep terminal stderr colorful, but keep persisted logs plain text.
        if isinstance(handler, StreamHandler) and getattr(handler, 'stream', None) == sys.stderr:
            handler.formatter.formatException = logging_format_exception_colored
        else:
            handler.formatter.formatException = logging_format_exception_plain


class BetExcLogger(Logger):
    def __init__(self, *args, **kwargs):
        super(BetExcLogger, self).__init__(*args, **kwargs)
        patch()
