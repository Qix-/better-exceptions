"""Opt-in IPython exception formatting, without an IPython dependency."""

import builtins

import better_exceptions


_STATE_ATTRIBUTE = '_better_exceptions_ipython_state'


def load_ipython_extension(ipython):
    if hasattr(ipython, _STATE_ATTRIBUTE):
        return

    previous_exceptions = ipython.custom_exceptions
    previous_handler = ipython.CustomTB

    def handler(shell, etype, value, tb, tb_offset=None):
        if isinstance(value, previous_exceptions):
            return previous_handler(etype, value, tb, tb_offset=tb_offset)

        # Keep IPython's special rendering (including remote tracebacks and
        # exception groups) rather than flattening it into a normal traceback.
        if (issubclass(etype, SyntaxError) or hasattr(value, '_render_traceback_')
                or isinstance(value, getattr(builtins, 'BaseExceptionGroup', ()))):
            shell.showtraceback((etype, value, tb), tb_offset=tb_offset)
            return []

        # Record the full traceback for %debug before trimming shell frames.
        shell._get_exc_info((etype, value, tb))
        visible_tb = tb
        offset = shell.InteractiveTB.tb_offset if tb_offset is None else tb_offset
        for _ in range(max(0, offset)):
            if visible_tb is not None:
                visible_tb = visible_tb.tb_next

        if visible_tb is None:
            shell.showtraceback((etype, value, tb), tb_offset=tb_offset)
            return []

        try:
            lines = better_exceptions.format_exception(etype, value, visible_tb)
        except Exception:
            shell.showtraceback((etype, value, tb), tb_offset=tb_offset)
            return []

        # Use the shell display path so terminal and notebook frontends receive
        # the traceback, rather than writing directly to the process stderr.
        shell._showtraceback(etype, value, lines)
        if shell.call_pdb:
            shell.debugger(force=True)
        return lines

    ipython.set_custom_exc((Exception,) + previous_exceptions, handler)
    setattr(ipython, _STATE_ATTRIBUTE,
            (previous_exceptions, previous_handler, ipython.CustomTB))


def unload_ipython_extension(ipython):
    state = getattr(ipython, _STATE_ATTRIBUTE, None)
    if state is None:
        return

    previous_exceptions, previous_handler, installed_handler = state
    # Another extension may have installed its own handler in the meantime.
    if ipython.CustomTB is installed_handler:
        ipython.custom_exceptions = previous_exceptions
        ipython.CustomTB = previous_handler
    delattr(ipython, _STATE_ATTRIBUTE)
