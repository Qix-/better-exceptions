from __future__ import absolute_import

from copy import copy
import sys

from logging import FileHandler, Logger, StreamHandler


FORMATTER_PATCHED = '_better_exceptions_patched'
FORMATTER_COLORED = '_better_exceptions_colored'


def _format_exception(exc_info, colored):
    from . import CAP_CHAR, MAX_LENGTH, PIPE_CHAR, THEME, format_exception
    from .formatter import ExceptionFormatter

    exc_type, value, _ = exc_info
    restore_args = exc_type is AssertionError
    args = value.args if restore_args else None

    try:
        if colored:
            return u''.join(format_exception(*exc_info))

        formatter = ExceptionFormatter(colored=False, theme=THEME, max_length=MAX_LENGTH,
                                       pipe_char=PIPE_CHAR, cap_char=CAP_CHAR)
        return u''.join(formatter.format_exception(*exc_info))
    finally:
        if restore_args:
            value.args = args


def _clone_formatter(formatter):
    formatter = copy(formatter)

    if getattr(formatter, FORMATTER_PATCHED, False):
        for name in ('format', 'formatException', FORMATTER_PATCHED, FORMATTER_COLORED):
            if name in formatter.__dict__:
                delattr(formatter, name)

    return formatter


def _patch_formatter(formatter, colored):
    if (getattr(formatter, FORMATTER_PATCHED, False) and
            getattr(formatter, FORMATTER_COLORED, None) == colored):
        return formatter

    formatter = _clone_formatter(formatter)
    format_record = formatter.format

    def formatException(exc_info):
        return _format_exception(exc_info, colored)

    def format(record):
        exc_text = record.exc_text
        record.exc_text = None
        try:
            return format_record(record)
        finally:
            record.exc_text = exc_text

    formatter.formatException = formatException
    formatter.format = format
    setattr(formatter, FORMATTER_PATCHED, True)
    setattr(formatter, FORMATTER_COLORED, colored)
    return formatter


def _handler_supports_color(handler):
    return isinstance(handler, StreamHandler) and handler.stream == sys.stderr


def _should_patch_handler(handler):
    return isinstance(handler, FileHandler) or _handler_supports_color(handler)


def patch():
    import logging

    for handler_ref in logging._handlerList:
        handler = handler_ref()
        if not _should_patch_handler(handler):
            continue

        colored = _handler_supports_color(handler)
        formatter = handler.formatter or logging._defaultFormatter
        handler.setFormatter(_patch_formatter(formatter, colored))


class BetExcLogger(Logger):
    def __init__(self, *args, **kwargs):
        super(BetExcLogger, self).__init__(*args, **kwargs)
        patch()
