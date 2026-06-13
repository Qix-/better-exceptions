import sys

from better_exceptions import ipython as bet_ipython


class FakeTB(object):
    def structured_traceback(self, etype, value, tb, tb_offset=None):
        return ['syntax']


class FakeIPython(object):
    def __init__(self):
        self.InteractiveTB = FakeTB()
        self.custom_exc = None

    def set_custom_exc(self, exc_tuple, handler):
        self.custom_exc = (exc_tuple, handler)


def test_load_ipython_extension_registers_exception_handler():
    shell = FakeIPython()

    bet_ipython.load_ipython_extension(shell)

    exc_tuple, handler = shell.custom_exc
    assert exc_tuple == (Exception,)
    assert handler is bet_ipython._showtraceback


def test_unload_ipython_extension_clears_exception_handler():
    shell = FakeIPython()

    bet_ipython.unload_ipython_extension(shell)

    assert shell.custom_exc == ((), None)


def test_showtraceback_returns_formatted_lines_for_regular_exceptions():
    shell = FakeIPython()
    try:
        raise ValueError('boom')
    except ValueError:
        etype, value, tb = sys.exc_info()

    lines = bet_ipython._showtraceback(shell, etype, value, tb)

    assert any('ValueError' in line for line in lines)
    assert any('boom' in line for line in lines)


def test_showtraceback_delegates_syntax_errors_to_ipython():
    shell = FakeIPython()

    lines = bet_ipython._showtraceback(shell, SyntaxError, SyntaxError('bad'), None)

    assert lines == ['syntax']


def test_patch_ipython_returns_false_without_shell():
    assert bet_ipython.patch_ipython(None) is False
