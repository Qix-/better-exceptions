import sys

import better_exceptions
from better_exceptions.integrations import ipython


class FakeShell(object):
    def __init__(self):
        self.calls = []
        self.stderr = []
        self.showtraceback = self.original_showtraceback

    def original_showtraceback(self, exc_tuple=None, filename=None, tb_offset=None,
                               exception_only=False, **kwargs):
        self.calls.append({
            'exc_tuple': exc_tuple,
            'filename': filename,
            'tb_offset': tb_offset,
            'exception_only': exception_only,
            'kwargs': kwargs,
        })
        return 'original'

    def write_err(self, data):
        self.stderr.append(data)
        return 'written'


class OldSignatureShell(FakeShell):
    def original_showtraceback(self, exc_tuple=None, filename=None, tb_offset=None,
                               exception_only=False):
        self.calls.append({
            'exc_tuple': exc_tuple,
            'filename': filename,
            'tb_offset': tb_offset,
            'exception_only': exception_only,
        })
        return 'old-original'


def make_error():
    try:
        value = 'ipython'
        raise RuntimeError(value)
    except RuntimeError:
        return sys.exc_info()


def test_install_and_uninstall_are_idempotent():
    shell = FakeShell()
    original = shell.showtraceback

    assert ipython.install(shell) is True
    assert ipython.install(shell) is False
    assert shell.showtraceback is not original

    assert ipython.uninstall(shell) is True
    assert ipython.uninstall(shell) is False
    assert shell.showtraceback is original


def test_ipython_traceback_uses_better_exceptions():
    shell = FakeShell()
    ipython.install(shell)

    result = shell.showtraceback(make_error())

    assert result == 'written'
    assert len(shell.calls) == 0
    assert 'RuntimeError' in shell.stderr[0]
    assert 'ipython' in shell.stderr[0]


def test_ipython_traceback_delegates_special_cases():
    cases = [
        {'filename': 'input.py'},
        {'tb_offset': 1},
        {'exception_only': True},
        {'running_compiled_code': True},
    ]

    for case in cases:
        shell = FakeShell()
        ipython.install(shell)

        kwargs = case.copy()
        result = shell.showtraceback(make_error(), **kwargs)

        assert result == 'original'
        assert len(shell.stderr) == 0
        assert len(shell.calls) == 1


def test_ipython_traceback_delegates_syntax_error():
    shell = FakeShell()
    ipython.install(shell)

    result = shell.showtraceback((SyntaxError, SyntaxError('bad syntax'), None))

    assert result == 'original'
    assert len(shell.stderr) == 0
    assert len(shell.calls) == 1


def test_ipython_traceback_supports_older_showtraceback_signatures():
    shell = OldSignatureShell()
    ipython.install(shell)

    result = shell.showtraceback(make_error(), running_compiled_code=True)

    assert result == 'old-original'
    assert len(shell.stderr) == 0
    assert len(shell.calls) == 1


def test_top_level_ipython_extension_delegates_to_integration():
    shell = FakeShell()

    better_exceptions.load_ipython_extension(shell)
    assert hasattr(shell, ipython._ORIGINAL_SHOWTRACEBACK)

    better_exceptions.unload_ipython_extension(shell)
    assert not hasattr(shell, ipython._ORIGINAL_SHOWTRACEBACK)


if __name__ == '__main__':
    for name, value in sorted(globals().items()):
        if name.startswith('test_') and callable(value):
            value()
