from __future__ import absolute_import

import io
import sys

import better_exceptions
from better_exceptions.integrations import ipython


class FakeIPython(object):
    def __init__(self):
        self.delegated = []

    def _get_exc_info(self, exc_tuple):
        return exc_tuple

    def showtraceback(self, exc_tuple=None, filename=None, tb_offset=None,
                      exception_only=False, **kwargs):
        self.delegated.append((exc_tuple, filename, tb_offset,
                               exception_only, kwargs))
        return 'delegated'


class FakeIPythonOld(object):
    def __init__(self):
        self.delegated = []

    def showtraceback(self, exc_tuple=None, filename=None, tb_offset=None,
                      exception_only=False):
        self.delegated.append((exc_tuple, filename, tb_offset, exception_only))
        return 'delegated-old'


def raise_runtime_error():
    value = 42
    raise RuntimeError('boom {}'.format(value))


def test_formats_regular_exceptions():
    stream = io.StringIO()

    old_stream = better_exceptions.STREAM
    old_should_encode = better_exceptions.SHOULD_ENCODE
    old_supports_color = better_exceptions.SUPPORTS_COLOR

    better_exceptions.STREAM = stream
    better_exceptions.SHOULD_ENCODE = False
    better_exceptions.SUPPORTS_COLOR = False

    try:
        shell = FakeIPython()
        assert ipython.install(shell) is True
        assert ipython.install(shell) is True

        try:
            raise_runtime_error()
        except RuntimeError:
            shell.showtraceback(sys.exc_info(), running_compiled_code=False)

        output = stream.getvalue()
        assert 'RuntimeError: boom 42' in output
        assert 'raise RuntimeError' in output
        assert not shell.delegated
    finally:
        better_exceptions.STREAM = old_stream
        better_exceptions.SHOULD_ENCODE = old_should_encode
        better_exceptions.SUPPORTS_COLOR = old_supports_color


def test_delegates_special_tracebacks():
    shell = FakeIPython()
    assert ipython.install(shell) is True

    syntax_tuple = (SyntaxError, SyntaxError('bad'), None)
    assert shell.showtraceback(syntax_tuple) == 'delegated'
    assert len(shell.delegated) == 1

    shell.delegated = []
    value_tuple = (ValueError, ValueError('x'), None)
    assert shell.showtraceback(value_tuple, exception_only=True) == 'delegated'
    assert len(shell.delegated) == 1


def test_old_ipython_signature_fallback():
    shell = FakeIPythonOld()
    assert ipython.install(shell) is True

    syntax_tuple = (SyntaxError, SyntaxError('bad'), None)
    assert shell.showtraceback(syntax_tuple, running_compiled_code=True) == 'delegated-old'
    assert len(shell.delegated) == 1


def test_uninstall_restores_showtraceback():
    shell = FakeIPython()
    old_show = shell.showtraceback

    assert ipython.install(shell) is True
    assert shell.showtraceback != old_show
    assert ipython.uninstall(shell) is True
    assert shell.showtraceback == old_show
    assert ipython.uninstall(shell) is False


def test_module_extension_hooks():
    shell = FakeIPython()
    better_exceptions.load_ipython_extension(shell)
    assert hasattr(shell, ipython.ORIGINAL_SHOWTRACEBACK_ATTR)

    better_exceptions.unload_ipython_extension(shell)
    assert not hasattr(shell, ipython.ORIGINAL_SHOWTRACEBACK_ATTR)


if __name__ == '__main__':
    test_formats_regular_exceptions()
    test_delegates_special_tracebacks()
    test_old_ipython_signature_fallback()
    test_uninstall_restores_showtraceback()
    test_module_extension_hooks()
