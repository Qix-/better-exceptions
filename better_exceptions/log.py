from __future__ import absolute_import

import sys

from logging import Logger, StreamHandler


def patch():
    import logging
    from . import format_exception

    def logging_format_exception(exc_info):
        return u''.join(format_exception(*exc_info))

    if hasattr(logging, '_defaultFormatter'):
        logging._defaultFormatter.format_exception = logging_format_exception

    # Patch StreamHandlers that write to stderr (the default logging stream).
    # We use colored output on TTYs, plain on file streams.
    patchables = [handler() for handler in logging._handlerList
                  if isinstance(handler(), StreamHandler)]
    patchables = [handler for handler in patchables
                  if handler.stream == sys.stderr]
    patchables = [handler for handler in patchables
                  if handler.formatter is not None]
    for handler in patchables:
        handler.formatter.formatException = logging_format_exception

    # For FileHandlers and StreamHandlers not writing to stderr,
    # override formatException to use plain (non-colored) output
    for handler_ref in logging._handlerList:
        handler = handler_ref()
        if not isinstance(handler, StreamHandler):
            continue
        if handler in patchables:
            continue  # already handled above
        if handler.formatter is None:
            continue
        # Check if this handler writes to a non-TTY (e.g. a file)
        try:
            is_tty = handler.stream.isatty()
        except (AttributeError, IOError):
            is_tty = False
        if not is_tty:
            handler.formatter.formatException = (
                lambda ei, _f=format_exception: u''.join(_f(*ei, colored=False))
            )


class BetExcLogger(Logger):
    def __init__(self, *args, **kwargs):
        super(BetExcLogger, self).__init__(*args, **kwargs)
        patch()
