import unittest

from better_exceptions.integrations import ipython


class FakeShell(object):
    def __init__(self):
        self.exc_types = None
        self.handler = None

    def set_custom_exc(self, exc_types, handler):
        self.exc_types = exc_types
        self.handler = handler


class IPythonIntegrationTest(unittest.TestCase):
    def test_returns_false_when_ipython_missing(self):
        original_import = __import__

        def fake_import(name, *args, **kwargs):
            if name == 'IPython':
                raise ImportError('missing')
            return original_import(name, *args, **kwargs)

        import builtins
        builtins_import = builtins.__import__
        builtins.__import__ = fake_import
        try:
            self.assertFalse(ipython.patch(lambda *args: None))
        finally:
            builtins.__import__ = builtins_import

    def test_returns_false_when_no_active_shell(self):
        shell_getter = ipython.__dict__.get('get_ipython')

        class DummyIPython(object):
            @staticmethod
            def get_ipython():
                return None

        import sys
        sys.modules['IPython'] = DummyIPython
        try:
            self.assertFalse(ipython.patch(lambda *args: None))
        finally:
            if shell_getter is not None:
                ipython.get_ipython = shell_getter

    def test_registers_custom_handler_and_calls_excepthook(self):
        calls = []
        shell = FakeShell()

        class DummyIPython(object):
            @staticmethod
            def get_ipython():
                return shell

        import sys
        previous = sys.modules.get('IPython')
        sys.modules['IPython'] = DummyIPython
        try:
            ok = ipython.patch(lambda et, ev, tb: calls.append((et, ev, tb)))
            self.assertTrue(ok)
            self.assertEqual(shell.exc_types, (BaseException,))
            err = RuntimeError('boom')
            result = shell.handler(shell, RuntimeError, err, None)
            self.assertTrue(result)
            self.assertEqual(len(calls), 1)
            self.assertIs(calls[0][0], RuntimeError)
            self.assertIs(calls[0][1], err)
        finally:
            if previous is not None:
                sys.modules['IPython'] = previous
            else:
                del sys.modules['IPython']


if __name__ == '__main__':
    unittest.main()
