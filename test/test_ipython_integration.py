"""Test the IPython integration for better_exceptions.

This tests the fix for issue #10: "ipython support"

The integration uses IPython's ``set_custom_exc`` API to install
better_exceptions as the exception formatter in IPython/Jupyter sessions.
"""
from __future__ import absolute_import

import sys
import unittest


def test_import_install():
    """The install function should be importable."""
    from better_exceptions.integrations.ipython import install
    assert callable(install)
    print("test_import_install: PASSED")


def test_no_active_shell():
    """install() should raise RuntimeError when no IPython shell is active."""
    from better_exceptions.integrations.ipython import install

    # get_ipython() returns None when not in an IPython session
    try:
        install()
        assert False, "Expected RuntimeError when no IPython shell is active"
    except RuntimeError as e:
        assert 'No active IPython shell' in str(e)
    except ImportError:
        # IPython is not installed - skip this test
        pass

    print("test_no_active_shell: PASSED")


def test_install_with_mock_shell():
    """install() should register handler via set_custom_exc."""
    from better_exceptions.integrations.ipython import install

    # We need to mock get_ipython to return an object with set_custom_exc
    # Since we can't easily do this with the real IPython, we'll test
    # by creating a fake IPython module
    import types

    # Save original modules
    original_ipython = sys.modules.get('IPython', None)

    # Create a fake IPython module
    fake_ipython = types.ModuleType('IPython')

    class MockShell:
        def __init__(self):
            self.registered_exceptions = None
            self.registered_handler = None

        def set_custom_exc(self, etype, handler):
            self.registered_exceptions = etype
            self.registered_handler = handler

    mock_shell = MockShell()

    def mock_get_ipython():
        return mock_shell

    fake_ipython.get_ipython = mock_get_ipython

    try:
        sys.modules['IPython'] = fake_ipython

        # Now install should work
        install()

        # Verify that set_custom_exc was called with BaseException
        assert mock_shell.registered_exceptions is not None
        assert BaseException in mock_shell.registered_exceptions
        assert mock_shell.registered_handler is not None
        assert callable(mock_shell.registered_handler)
    finally:
        # Restore original modules
        if original_ipython is not None:
            sys.modules['IPython'] = original_ipython
        else:
            sys.modules.pop('IPython', None)

    print("test_install_with_mock_shell: PASSED")


def test_handler_formats_exception():
    """The registered handler should format exceptions using better_exceptions."""
    from better_exceptions.integrations.ipython import install

    import types

    original_ipython = sys.modules.get('IPython', None)

    class MockShell:
        def __init__(self):
            self.registered_handler = None

        def set_custom_exc(self, etype, handler):
            self.registered_exceptions = etype
            self.registered_handler = handler

        def showtraceback(self):
            pass

    mock_shell = MockShell()

    fake_ipython = types.ModuleType('IPython')
    fake_ipython.get_ipython = lambda: mock_shell

    try:
        sys.modules['IPython'] = fake_ipython
        install()

        handler = mock_shell.registered_handler
        assert handler is not None

        # Simulate an exception
        try:
            x = 42
            raise ValueError('test ipython handler')
        except ValueError:
            etype, value, tb = sys.exc_info()

        # Capture stderr
        import io
        old_stderr = sys.stderr
        sys.stderr = captured = io.StringIO()

        try:
            # Call the handler - should print formatted exception to stderr
            handler(mock_shell, etype, value, tb)
        finally:
            sys.stderr = old_stderr

        output = captured.getvalue()

        # The output should contain the exception info
        assert 'ValueError' in output
        assert 'test ipython handler' in output
    finally:
        if original_ipython is not None:
            sys.modules['IPython'] = original_ipython
        else:
            sys.modules.pop('IPython', None)

    print("test_handler_formats_exception: PASSED")


def test_syntax_error_delegates_to_shell():
    """SyntaxError should be delegated to IPython's showtraceback."""
    from better_exceptions.integrations.ipython import install

    import types

    original_ipython = sys.modules.get('IPython', None)

    class MockShell:
        def __init__(self):
            self.showtraceback_called = False
            self.registered_handler = None

        def set_custom_exc(self, etype, handler):
            self.registered_exceptions = etype
            self.registered_handler = handler

        def showtraceback(self):
            self.showtraceback_called = True

    mock_shell = MockShell()

    fake_ipython = types.ModuleType('IPython')
    fake_ipython.get_ipython = lambda: mock_shell

    try:
        sys.modules['IPython'] = fake_ipython
        install()

        handler = mock_shell.registered_handler

        # Simulate a SyntaxError
        try:
            exec('this is not valid python')
        except SyntaxError:
            etype, value, tb = sys.exc_info()

        handler(mock_shell, etype, value, tb)

        assert mock_shell.showtraceback_called, \
            "SyntaxError should delegate to shell.showtraceback()"
    finally:
        if original_ipython is not None:
            sys.modules['IPython'] = original_ipython
        else:
            sys.modules.pop('IPython', None)

    print("test_syntax_error_delegates_to_shell: PASSED")


if __name__ == '__main__':
    test_import_install()
    test_no_active_shell()
    test_install_with_mock_shell()
    test_handler_formats_exception()
    test_syntax_error_delegates_to_shell()
    print("\nAll tests passed!")
