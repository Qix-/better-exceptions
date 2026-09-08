from __future__ import absolute_import

import better_exceptions
from better_exceptions.integrations import ipython


class FakeIPython(object):
    def __init__(self):
        self.custom_exceptions = (LookupError,)
        self.CustomTB = self.original_handler

    def original_handler(self, exc_type, value, traceback, tb_offset=None):
        return ['original']

    def set_custom_exc(self, exc_tuple, handler):
        self.custom_exceptions = exc_tuple
        self.CustomTB = lambda exc_type, value, traceback, tb_offset=None: handler(
            self, exc_type, value, traceback, tb_offset=tb_offset)


def test_extension_formats_exception():
    shell = FakeIPython()
    better_exceptions.load_ipython_extension(shell)

    try:
        marker = 42
        raise RuntimeError('boom {}'.format(marker))
    except RuntimeError as error:
        formatted = shell.CustomTB(RuntimeError, error, error.__traceback__)

    output = ''.join(formatted)
    assert shell.custom_exceptions == (Exception,)
    assert 'RuntimeError: boom 42' in output
    assert 'marker' in output
    assert '42' in output


def test_extension_is_idempotent_and_restores_previous_handler():
    shell = FakeIPython()
    previous_exceptions = shell.custom_exceptions
    previous_handler = shell.CustomTB

    better_exceptions.load_ipython_extension(shell)
    better_exceptions.load_ipython_extension(shell)
    better_exceptions.unload_ipython_extension(shell)

    assert shell.custom_exceptions == previous_exceptions
    assert shell.CustomTB == previous_handler

    better_exceptions.unload_ipython_extension(shell)
    assert shell.custom_exceptions == previous_exceptions
    assert shell.CustomTB == previous_handler


if __name__ == '__main__':
    test_extension_formats_exception()
    test_extension_is_idempotent_and_restores_previous_handler()
