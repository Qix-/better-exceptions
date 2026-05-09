from __future__ import absolute_import

import sys
import types

from .. import excepthook


ORIGINAL_SHOWTRACEBACK_ATTR = '_better_exceptions_showtraceback'


def _get_running_ipython():
    try:
        from IPython import get_ipython
    except ImportError:
        try:
            import builtins
        except ImportError:
            import __builtin__ as builtins

        get_ipython = getattr(builtins, 'get_ipython', None)

    return get_ipython() if get_ipython is not None else None


def _bind(method, instance):
    try:
        return types.MethodType(method, instance)
    except TypeError:
        return types.MethodType(method, instance, type(instance))


def _delegate(old_showtraceback, exc_tuple, filename, tb_offset,
              exception_only, kwargs):
    try:
        return old_showtraceback(exc_tuple, filename, tb_offset,
                                 exception_only, **kwargs)
    except TypeError:
        if kwargs:
            return old_showtraceback(exc_tuple, filename, tb_offset,
                                     exception_only)
        raise


def _normalize_exc_info(ipython, exc_tuple):
    if exc_tuple is None:
        exc_tuple = sys.exc_info()

    if hasattr(ipython, '_get_exc_info'):
        return ipython._get_exc_info(exc_tuple)

    return exc_tuple


def _can_format_with_better_exceptions(exc_type, filename, tb_offset,
                                       exception_only):
    if filename is not None or tb_offset is not None or exception_only:
        return False

    try:
        if issubclass(exc_type, SyntaxError):
            return False
    except TypeError:
        return False

    return True


def _showtraceback(self, exc_tuple=None, filename=None, tb_offset=None,
                   exception_only=False, **kwargs):
    original_exc_tuple = exc_tuple
    exc_type, value, traceback = _normalize_exc_info(self, exc_tuple)
    old_showtraceback = getattr(self, ORIGINAL_SHOWTRACEBACK_ATTR)

    if _can_format_with_better_exceptions(exc_type, filename, tb_offset,
                                          exception_only):
        return excepthook(exc_type, value, traceback)

    return _delegate(old_showtraceback, original_exc_tuple, filename,
                     tb_offset, exception_only, kwargs)


def install(ipython=None):
    ipython = ipython or _get_running_ipython()
    if ipython is None:
        return False

    if hasattr(ipython, ORIGINAL_SHOWTRACEBACK_ATTR):
        return True

    setattr(ipython, ORIGINAL_SHOWTRACEBACK_ATTR, ipython.showtraceback)
    ipython.showtraceback = _bind(_showtraceback, ipython)
    return True


def uninstall(ipython=None):
    ipython = ipython or _get_running_ipython()
    if ipython is None or not hasattr(ipython, ORIGINAL_SHOWTRACEBACK_ATTR):
        return False

    ipython.showtraceback = getattr(ipython, ORIGINAL_SHOWTRACEBACK_ATTR)
    delattr(ipython, ORIGINAL_SHOWTRACEBACK_ATTR)
    return True


def load_ipython_extension(ipython):
    install(ipython)


def unload_ipython_extension(ipython):
    uninstall(ipython)
