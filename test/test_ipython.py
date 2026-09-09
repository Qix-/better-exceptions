"""Integration tests: python -m unittest discover -s test -p test_ipython.py."""

import contextlib
import io
import sys
import tempfile
import unittest
from unittest.mock import patch

from IPython.core.interactiveshell import InteractiveShell
from traitlets.config import Config

import better_exceptions


class IPythonTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        config = Config()
        config.HistoryManager.enabled = False
        config.HistoryManager.hist_file = ':memory:'
        self.shell = InteractiveShell(config=config, ipython_dir=self.directory.name)
        self.addCleanup(self.directory.cleanup)
        self.colors = patch.object(better_exceptions, 'SUPPORTS_COLOR', False)
        self.colors.start()
        self.addCleanup(self.colors.stop)

    def load(self):
        result = self.shell.extension_manager.load_extension('better_exceptions')
        self.assertIsNone(result)
        self.addCleanup(self.shell.extension_manager.unload_extension, 'better_exceptions')

    def run_cell(self, code):
        output = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            result = self.shell.run_cell(code)
        return result, output.getvalue()

    def test_runtime_error_shows_values_and_hides_shell_frame(self):
        self.load()
        result, output = self.run_cell('divisor = 0\n42 / divisor')
        self.assertIsInstance(result.error_in_exec, ZeroDivisionError)
        self.assertIn('ZeroDivisionError', output)
        self.assertIn('42 / divisor', output)
        self.assertIn(better_exceptions.CAP_CHAR + ' 0', output)
        self.assertNotIn('interactiveshell.py', output)
        self.assertIs(sys.last_value, result.error_in_exec)
        self.assertIsNotNone(sys.last_traceback)

    def test_syntax_error_keeps_ipython_renderer(self):
        self.load()
        with patch.object(better_exceptions, 'format_exception') as formatter:
            result, output = self.run_cell('if True print("broken")')
        self.assertIsInstance(result.error_before_exec, SyntaxError)
        self.assertIn('SyntaxError', output)
        formatter.assert_not_called()

    def test_runtime_syntax_error_keeps_ipython_renderer(self):
        self.load()
        with patch.object(better_exceptions, 'format_exception') as formatter:
            _, output = self.run_cell('compile("if True print(1)", "example.py", "exec")')
        self.assertIn('SyntaxError', output)
        formatter.assert_not_called()

    def test_formatter_failure_shows_original_exception(self):
        self.load()
        with patch.object(better_exceptions, 'format_exception', side_effect=RuntimeError('formatter failed')):
            _, output = self.run_cell('1 / 0')
        self.assertIn('ZeroDivisionError', output)
        self.assertNotIn('formatter failed', output)
        self.assertNotIn('Custom TB Handler failed', output)

    def test_debugger_is_called(self):
        self.load()
        self.shell.call_pdb = True
        with patch.object(self.shell, 'debugger') as debugger:
            self.run_cell('1 / 0')
        debugger.assert_called_once_with(force=True)

    def test_existing_custom_handler_is_preserved(self):
        calls = []

        def handler(shell, etype, value, tb, tb_offset=None):
            calls.append(value)
            return ['custom error']

        self.shell.set_custom_exc((ValueError,), handler)
        original = self.shell.CustomTB
        self.load()
        result, _ = self.run_cell('raise ValueError("custom")')
        self.assertEqual(calls, [result.error_in_exec])
        self.shell.extension_manager.unload_extension('better_exceptions')
        self.assertIs(self.shell.CustomTB, original)
        self.assertEqual(self.shell.custom_exceptions, (ValueError,))

    def test_unload_does_not_overwrite_later_handler(self):
        self.load()
        self.shell.set_custom_exc((ValueError,), lambda *args, **kwargs: [])
        replacement = self.shell.CustomTB
        self.shell.extension_manager.unload_extension('better_exceptions')
        self.assertIs(self.shell.CustomTB, replacement)

    def test_reload_and_unload(self):
        original = self.shell.CustomTB
        original_exceptions = self.shell.custom_exceptions
        self.load()
        self.shell.extension_manager.reload_extension('better_exceptions')
        _, output = self.run_cell('1 / 0')
        self.assertEqual(output.count('ZeroDivisionError'), 1)
        self.shell.extension_manager.unload_extension('better_exceptions')
        self.assertIs(self.shell.CustomTB, original)
        self.assertEqual(self.shell.custom_exceptions, original_exceptions)

    def test_chained_exception(self):
        self.load()
        _, output = self.run_cell('try:\n    1 / 0\nexcept ZeroDivisionError as error:\n    raise ValueError("outer") from error')
        self.assertIn('ZeroDivisionError', output)
        self.assertIn('direct cause', output)
        self.assertIn('ValueError: outer', output)

    def test_traceback_offset(self):
        self.load()
        try:
            1 / 0
        except ZeroDivisionError:
            info = sys.exc_info()
        with patch.object(self.shell, '_showtraceback') as display:
            lines = self.shell.CustomTB(*info, tb_offset=0)
        self.assertIn('test_ipython.py', ''.join(lines))
        display.assert_called_once_with(info[0], info[1], lines)

    def test_custom_exception_renderer(self):
        self.load()
        with patch.object(better_exceptions, 'format_exception') as formatter:
            _, output = self.run_cell(
                'class CustomError(Exception):\n'
                '    def _render_traceback_(self):\n'
                '        return ["CUSTOM TRACEBACK"]\n'
                'raise CustomError()')
        self.assertIn('CUSTOM TRACEBACK', output)
        formatter.assert_not_called()

    @unittest.skipIf(sys.version_info < (3, 11), 'ExceptionGroup requires Python 3.11')
    def test_exception_group_keeps_nested_errors(self):
        self.load()
        with patch.object(better_exceptions, 'format_exception') as formatter:
            _, output = self.run_cell('raise ExceptionGroup("errors", [ValueError("first"), TypeError("second")])')
        self.assertIn('ValueError: first', output)
        self.assertIn('TypeError: second', output)
        formatter.assert_not_called()

    def test_existing_base_exception_handler_is_preserved(self):
        calls = []

        def handler(shell, etype, value, tb, tb_offset=None):
            calls.append(value)
            return []

        self.shell.set_custom_exc((KeyboardInterrupt,), handler)
        self.load()
        result, _ = self.run_cell('raise KeyboardInterrupt()')
        self.assertEqual(calls, [result.error_in_exec])

    def test_loading_extension_does_not_change_global_excepthook(self):
        original = sys.excepthook
        self.load()
        self.assertIs(sys.excepthook, original)


if __name__ == '__main__':
    unittest.main()
