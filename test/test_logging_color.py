"""Test that logged exceptions respect stream TTY status for color output.

This tests the fix for issue #87: "Logged exceptions shouldn't contain colour"

The issue: when the terminal supports colors (FORCE_COLOR=1 or terminal with
color support), exceptions logged through the logging module to non-TTY streams
(e.g. files) would contain ANSI escape codes, making them hard to read in
editors.

The fix: ``_stream_supports_color()`` checks both the global ``SUPPORTS_COLOR``
flag *and* whether the specific stream is a TTY. The ``FORCE_COLOR=1``
environment variable acts as an explicit override that enables color regardless
of TTY status.
"""
from __future__ import absolute_import

import io
import logging
import os
import sys
import tempfile

import better_exceptions
from better_exceptions.log import _stream_supports_color, _make_logging_format_exception


def _with_env(key, value, fn):
    """Run *fn* with *key* temporarily set to *value* in the environment."""
    old = os.environ.get(key)
    sentinel = object()
    if value is None:
        os.environ.pop(key, None)
    else:
        os.environ[key] = value
    try:
        return fn()
    finally:
        if old is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = old


def test_non_tty_stream_no_color():
    """Non-TTY streams must not contain color codes when FORCE_COLOR is unset."""
    def run():
        # Ensure FORCE_COLOR is NOT set so the TTY check applies
        os.environ.pop('FORCE_COLOR', None)

        buf = io.StringIO()

        handler = logging.StreamHandler(buf)
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(logging.Formatter('%(message)s'))
        handler.formatter.formatException = _make_logging_format_exception(buf)

        logger = logging.getLogger('test_non_tty')
        logger.setLevel(logging.DEBUG)
        logger.handlers = []
        logger.addHandler(handler)

        try:
            x = 42
            raise ValueError('test error')
        except:
            logger.exception('something went wrong')

        content = buf.getvalue()

        assert '\x1b[' not in content, \
            "Log output to non-TTY stream should not contain ANSI color codes. " \
            "Got: {!r}".format(content[:200])

        assert 'ValueError' in content
        assert 'test error' in content

    _with_env('FORCE_COLOR', None, run)
    print("test_non_tty_stream_no_color: PASSED")


def test_force_color_overrides_tty_check():
    """FORCE_COLOR=1 enables color even for non-TTY streams."""
    def run():
        buf = io.StringIO()
        result = _stream_supports_color(buf)
        assert result is True, \
            "FORCE_COLOR=1 should enable color even for non-TTY streams"

    _with_env('FORCE_COLOR', '1', run)
    print("test_force_color_overrides_tty_check: PASSED")


def test_no_force_color_non_tty_no_color():
    """Without FORCE_COLOR, non-TTY streams should not get color."""
    def run():
        buf = io.StringIO()
        result = _stream_supports_color(buf)
        assert result is False, \
            "Non-TTY stream without FORCE_COLOR should not support color. " \
            "SUPPORTS_COLOR={}, result={}".format(
                better_exceptions.SUPPORTS_COLOR, result)

    _with_env('FORCE_COLOR', None, run)
    print("test_no_force_color_non_tty_no_color: PASSED")


def test_file_handler_no_color():
    """FileHandler output must not contain color codes (no FORCE_COLOR)."""
    def run():
        tmpfile = tempfile.NamedTemporaryFile(
            mode='w', suffix='.log', delete=False)
        tmpfile.close()

        try:
            fh = logging.FileHandler(tmpfile.name)
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(logging.Formatter('%(message)s'))
            fh.formatter.formatException = _make_logging_format_exception(fh.stream)

            logger = logging.getLogger('test_file_handler')
            logger.setLevel(logging.DEBUG)
            logger.handlers = []
            logger.addHandler(fh)

            try:
                x = 42
                raise ValueError('file handler test')
            except:
                logger.exception('error in file')

            with open(tmpfile.name, 'r') as f:
                content = f.read()

            assert '\x1b[' not in content, \
                "FileHandler output should not contain ANSI color codes. " \
                "Got: {!r}".format(content[:200])

            assert 'ValueError' in content
            assert 'file handler test' in content
        finally:
            os.unlink(tmpfile.name)

    _with_env('FORCE_COLOR', None, run)
    print("test_file_handler_no_color: PASSED")


def test_force_color_file_handler_has_color():
    """With FORCE_COLOR=1, even file output gets color (explicit override)."""
    def run():
        buf = io.StringIO()
        handler = logging.StreamHandler(buf)
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(logging.Formatter('%(message)s'))
        handler.formatter.formatException = _make_logging_format_exception(buf)

        logger = logging.getLogger('test_force_color_file')
        logger.setLevel(logging.DEBUG)
        logger.handlers = []
        logger.addHandler(handler)

        try:
            raise ValueError('force color test')
        except:
            logger.exception('forced color')

        content = buf.getvalue()
        assert '\x1b[' in content, \
            "With FORCE_COLOR=1, output should contain ANSI color codes. " \
            "Got: {!r}".format(content[:200])

    _with_env('FORCE_COLOR', '1', run)
    print("test_force_color_file_handler_has_color: PASSED")


if __name__ == '__main__':
    test_non_tty_stream_no_color()
    test_force_color_overrides_tty_check()
    test_no_force_color_non_tty_no_color()
    test_file_handler_no_color()
    test_force_color_file_handler_has_color()
    print("\nAll tests passed!")
