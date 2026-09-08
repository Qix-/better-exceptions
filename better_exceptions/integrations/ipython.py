"""IPython extension support for :mod:`better_exceptions`.

IPython does not use ``sys.excepthook`` for exceptions raised by executed
cells.  Its public ``set_custom_exc`` hook is the supported way for an
extension to provide a traceback formatter.
"""

from __future__ import absolute_import


_SAVED_HANDLER = '_better_exceptions_saved_custom_handler'


def _format_exception(shell, exc_type, value, traceback, tb_offset=None):
    del shell, tb_offset

    from better_exceptions import format_exception
    return format_exception(exc_type, value, traceback)


def load_ipython_extension(ipython):
    """Install the formatter in an IPython shell.

    Preserve any existing custom exception handler so unloading the extension
    does not disturb another extension.
    """
    if hasattr(ipython, _SAVED_HANDLER):
        return

    previous = (
        getattr(ipython, 'custom_exceptions', ()),
        getattr(ipython, 'CustomTB', None),
    )
    ipython.set_custom_exc((Exception,), _format_exception)
    setattr(ipython, _SAVED_HANDLER, previous)


def unload_ipython_extension(ipython):
    """Restore the custom exception handler that preceded this extension."""
    if not hasattr(ipython, _SAVED_HANDLER):
        return

    previous_exceptions, previous_handler = getattr(ipython, _SAVED_HANDLER)
    delattr(ipython, _SAVED_HANDLER)

    # ``set_custom_exc`` binds plain callables.  ``CustomTB`` is already a
    # bound method, so restore the two pieces of state directly.
    ipython.custom_exceptions = previous_exceptions
    ipython.CustomTB = previous_handler
