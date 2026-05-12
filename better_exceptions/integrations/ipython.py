from __future__ import absolute_import

import sys
import types

import better_exceptions


ORIGINAL_SHOWTRACEBACK = '_better_exceptions_original_showtraceback'


def _get_ipython():
    try:
        from IPython import get_ipython
    except ImportError:
        return None

    return get_ipython()


def _showtraceback(self, exc_tuple=None, filename=None, tb_offset=None,
                   exception_only=False, **kwargs):
    original_showtraceback = getattr(self, ORIGINAL_SHOWTRACEBACK)
    exc_tuple = exc_tuple or sys.exc_info()

    try:
        etype, value, tb = self._get_exc_info(exc_tuple)
    except AttributeError:
        etype, value, tb = exc_tuple

    use_better_exceptions = (
        filename is None and
        tb_offset is None and
        not exception_only and
        not issubclass(etype, SyntaxError)
    )

    if use_better_exceptions:
        return better_exceptions.excepthook(etype, value, tb)

    return original_showtraceback(
        exc_tuple, filename, tb_offset, exception_only, **kwargs
    )


def hook(ipython=None):
    ipython = ipython or _get_ipython()
    if ipython is None:
        raise RuntimeError('IPython shell not found')

    if not hasattr(ipython, ORIGINAL_SHOWTRACEBACK):
        setattr(ipython, ORIGINAL_SHOWTRACEBACK, ipython.showtraceback)

    ipython.showtraceback = types.MethodType(_showtraceback, ipython)
    return ipython


def unhook(ipython=None):
    ipython = ipython or _get_ipython()
    if ipython is None or not hasattr(ipython, ORIGINAL_SHOWTRACEBACK):
        return ipython

    ipython.showtraceback = getattr(ipython, ORIGINAL_SHOWTRACEBACK)
    delattr(ipython, ORIGINAL_SHOWTRACEBACK)
    return ipython


def load_ipython_extension(ipython):
    hook(ipython)


def unload_ipython_extension(ipython):
    unhook(ipython)
