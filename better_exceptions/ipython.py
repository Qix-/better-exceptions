"""IPython integration for better_exceptions.

Load with::

    %load_ext better_exceptions.ipython

or add ``c.InteractiveShellApp.extensions = ['better_exceptions.ipython']``
to an IPython profile.
"""

from __future__ import absolute_import
from __future__ import print_function

import sys

from . import format_exception


def _format_ipython_exception(etype, value, tb):
    """Return a list compatible with IPython's custom exception API."""
    return u''.join(format_exception(etype, value, tb)).splitlines(True)


def _showtraceback(shell, etype, value, tb, tb_offset=None):
    """IPython custom exception handler.

    IPython expects custom handlers to return a structured traceback, which
    is a list of display lines. Returning better_exceptions' formatted lines
    lets IPython keep owning display while we provide the formatter.
    """
    if issubclass(etype, SyntaxError):
        return shell.InteractiveTB.structured_traceback(etype, value, tb, tb_offset=tb_offset)
    return _format_ipython_exception(etype, value, tb)


def load_ipython_extension(ipython):
    """Register better_exceptions as IPython's exception formatter."""
    ipython.set_custom_exc((Exception,), _showtraceback)


def unload_ipython_extension(ipython):
    """Remove the custom exception formatter when the extension is unloaded."""
    ipython.set_custom_exc((), None)


def patch_ipython(ipython=None):
    """Programmatic helper for users who do not want to use ``%load_ext``."""
    if ipython is None:
        try:
            from IPython import get_ipython
        except ImportError:
            return False
        ipython = get_ipython()
    if ipython is None:
        return False
    load_ipython_extension(ipython)
    return True
