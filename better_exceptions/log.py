from __future__ import absolute_import

import sys

from logging import Logger, StreamHandler


def _isolate_exc_text(formatter):
    """Stop this formatter's cached ``record.exc_text`` from leaking into a
    DIFFERENT handler's formatter (fixes #87).

    Python's ``logging.Formatter.format()`` caches the formatted exception
    text directly on the record the first time any handler formats it (see
    the stdlib's own ``if not record.exc_text: record.exc_text =
    self.formatException(...)``). If handler A colorizes it first (e.g. our
    patched stderr handler), handler B -- say a plain ``FileHandler`` with
    its own, unrelated formatter -- reuses that same cached, colorized text
    instead of computing its own, because the cache lives on the shared
    record object, not per-handler.

    Restoring ``exc_text`` back to whatever it was BEFORE this formatter
    ran -- not unconditionally to ``None`` -- forces every other handler to
    independently recompute its own exception text in the common case
    (nothing had set it yet), while never destroying a value some other,
    unrelated piece of code may have legitimately pre-populated on the
    record for its own reasons before any handler touched it. Done in a
    ``try/finally`` so the restore happens even if the wrapped ``format()``
    call itself raises -- otherwise a mid-formatting exception would leave
    a colorized ``exc_text`` cached and ready to leak into the next
    handler exactly like the bug this is fixing. Idempotent: safe to call
    more than once per formatter (``patch()`` runs again for every new
    logger).
    """
    if getattr(formatter, '_better_exceptions_isolated', False):
        return
    original_format = formatter.format

    def format(record):
        original_exc_text = record.exc_text
        try:
            return original_format(record)
        finally:
            record.exc_text = original_exc_text

    formatter.format = format
    formatter._better_exceptions_isolated = True


def patch():
    import logging
    from . import format_exception

    logging_format_exception = lambda exc_info: u''.join(format_exception(*exc_info))

    if hasattr(logging, '_defaultFormatter'):
        logging._defaultFormatter.format_exception = logging_format_exception
        _isolate_exc_text(logging._defaultFormatter)

    handlers = [handler() for handler in logging._handlerList if isinstance(handler(), StreamHandler)]
    handlers = [handler for handler in handlers if handler.formatter is not None]

    # Any handler's cached exc_text can leak into any OTHER handler sharing
    # the same log record, regardless of which one is actually colorized --
    # isolate every handler we see, not just the stderr ones below.
    for handler in handlers:
        _isolate_exc_text(handler.formatter)

    stderr_handlers = [handler for handler in handlers if handler.stream == sys.stderr]
    for handler in stderr_handlers:
        handler.formatter.formatException = logging_format_exception


class BetExcLogger(Logger):
    def __init__(self, *args, **kwargs):
        super(BetExcLogger, self).__init__(*args, **kwargs)
        patch()
