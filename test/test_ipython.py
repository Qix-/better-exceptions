from __future__ import absolute_import

import io
import sys

import better_exceptions
from better_exceptions.integrations import ipython


class FakeIPython(object):
    def __init__(self):
        self.calls = []

    def _get_exc_info(self, exc_tuple):
        return exc_tuple

    def showtraceback(self, exc_tuple=None, filename=None, tb_offset=None,
                      exception_only=False, **kwargs):
        self.calls.append((exc_tuple, filename, tb_offset, exception_only, kwargs))
        return 'fallback'


def fail():
    value = 42
    raise ValueError(value)


def capture_better_exceptions():
    old_stream = better_exceptions.STREAM
    old_should_encode = better_exceptions.SHOULD_ENCODE
    old_supports_color = better_exceptions.SUPPORTS_COLOR

    better_exceptions.STREAM = io.StringIO()
    better_exceptions.SHOULD_ENCODE = False
    better_exceptions.SUPPORTS_COLOR = False

    return old_stream, old_should_encode, old_supports_color


def restore_better_exceptions(state):
    better_exceptions.STREAM = state[0]
    better_exceptions.SHOULD_ENCODE = state[1]
    better_exceptions.SUPPORTS_COLOR = state[2]


def test_formats_regular_exceptions():
    shell = ipython.hook(FakeIPython())
    state = capture_better_exceptions()

    try:
        try:
            fail()
        except ValueError:
            shell.showtraceback(sys.exc_info())

        output = better_exceptions.STREAM.getvalue()
        assert 'ValueError: 42' in output
        assert '-> 42' in output
        assert shell.calls == []
    finally:
        restore_better_exceptions(state)


def test_delegates_special_traceback_modes():
    shell = ipython.hook(FakeIPython())
    try:
        raise SyntaxError('bad')
    except SyntaxError:
        result = shell.showtraceback(sys.exc_info())

    assert result == 'fallback'
    assert len(shell.calls) == 1


def test_unhook_restores_original_showtraceback():
    shell = FakeIPython()
    original_showtraceback = shell.showtraceback

    ipython.hook(shell)
    assert shell.showtraceback != original_showtraceback

    ipython.unhook(shell)
    assert shell.showtraceback == original_showtraceback
    assert shell.showtraceback() == 'fallback'


if __name__ == '__main__':
    test_formats_regular_exceptions()
    test_delegates_special_traceback_modes()
    test_unhook_restores_original_showtraceback()
