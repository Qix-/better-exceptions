"""IPython integration for better_exceptions."""

from __future__ import absolute_import

import sys

import better_exceptions


_ORIGINAL_SHOWTRACEBACK = '_better_exceptions_original_showtraceback'


def load_ipython_extension(ipython):
    install(ipython)


def unload_ipython_extension(ipython):
    uninstall(ipython)


def install(ipython=None):
    if ipython is None:
        ipython = _get_ipython()
    if ipython is None:
        return False
    if hasattr(ipython, _ORIGINAL_SHOWTRACEBACK):
        return False

    original_showtraceback = ipython.showtraceback
    setattr(ipython, _ORIGINAL_SHOWTRACEBACK, original_showtraceback)

    def showtraceback(exc_tuple=None, filename=None, tb_offset=None,
                      exception_only=False, **kwargs):
        if _should_delegate(exc_tuple, filename, tb_offset, exception_only, kwargs):
            return _call_original(original_showtraceback, exc_tuple, filename,
                                  tb_offset, exception_only, kwargs)

        exc, value, tb = exc_tuple or sys.exc_info()
        formatted = ''.join(better_exceptions.format_exception(exc, value, tb))
        write_err = getattr(ipython, 'write_err', None)
        if write_err is not None:
            return write_err(formatted)
        return better_exceptions.write_stream(formatted)

    ipython.showtraceback = showtraceback
    return True


def uninstall(ipython=None):
    if ipython is None:
        ipython = _get_ipython()
    if ipython is None or not hasattr(ipython, _ORIGINAL_SHOWTRACEBACK):
        return False

    ipython.showtraceback = getattr(ipython, _ORIGINAL_SHOWTRACEBACK)
    delattr(ipython, _ORIGINAL_SHOWTRACEBACK)
    return True


def _get_ipython():
    try:
        from IPython import get_ipython
    except ImportError:
        return None
    return get_ipython()


def _should_delegate(exc_tuple, filename, tb_offset, exception_only, kwargs):
    if filename is not None or tb_offset is not None or exception_only:
        return True
    if kwargs.get('running_compiled_code'):
        return True

    exc, _, _ = exc_tuple or sys.exc_info()
    return exc is None or (isinstance(exc, type) and issubclass(exc, SyntaxError))


def _call_original(original_showtraceback, exc_tuple, filename, tb_offset,
                   exception_only, kwargs):
    try:
        return original_showtraceback(
            exc_tuple=exc_tuple,
            filename=filename,
            tb_offset=tb_offset,
            exception_only=exception_only,
            **kwargs
        )
    except TypeError:
        return original_showtraceback(exc_tuple, filename, tb_offset, exception_only)
