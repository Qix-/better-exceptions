from __future__ import absolute_import


def patch(excepthook):
    """Register better_exceptions inside an active IPython shell.

    Returns:
        bool: True when an IPython shell was detected and patched.
    """
    try:
        from IPython import get_ipython
    except ImportError:
        return False

    shell = get_ipython()
    if shell is None or not hasattr(shell, 'set_custom_exc'):
        return False

    def _custom_exc(shell, exc_type, value, tb, tb_offset=None):
        # IPython expects a truthy return value when the exception is fully handled.
        excepthook(exc_type, value, tb)
        return True

    shell.set_custom_exc((BaseException,), _custom_exc)
    return True
