"""IPython integration for better_exceptions.

This module provides a function to install better_exceptions as the
exception formatter in IPython/Jupyter environments.

Usage:
    In an IPython session or Jupyter notebook::

        from better_exceptions.integrations.ipython import install
        install()

    Or add the following to your IPython startup file
    (``~/.ipython/profile_default/startup/00-better_exceptions.py``)::

        try:
            from better_exceptions.integrations.ipython import install
            install()
        except ImportError:
            pass
"""

from __future__ import absolute_import

import sys


def install():
    """Install better_exceptions as IPython's exception formatter.

    This hooks into IPython's ``set_custom_exc`` mechanism to replace the
    default traceback formatter with better_exceptions' formatter for all
    exception types (except ``SyntaxError``, which IPython handles specially).
    """
    try:
        from IPython import get_ipython
    except ImportError:
        raise ImportError(
            'IPython is not available. Install it with: pip install ipython'
        )

    ip = get_ipython()
    if ip is None:
        raise RuntimeError(
            'No active IPython shell found. '
            'This function must be called from within an IPython/Jupyter session.'
        )

    import better_exceptions

    def better_exceptions_handler(shell, etype, value, tb, tb_offset=0):
        """Custom exception handler that uses better_exceptions formatting."""
        # Let IPython handle SyntaxErrors with its own special formatting
        if issubclass(etype, SyntaxError):
            shell.showtraceback()
            return

        # Use better_exceptions to format and display the exception
        formatted = better_exceptions.format_exception(etype, value, tb)
        output = ''.join(formatted)

        # Write to the shell's output stream
        # Use print so it goes through IPython's display system
        print(output, file=sys.stderr)

    # Register the handler for all exceptions
    ip.set_custom_exc((BaseException,), better_exceptions_handler)
