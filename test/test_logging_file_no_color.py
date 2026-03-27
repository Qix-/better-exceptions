"""Verify that exceptions logged to files do not contain ANSI escape codes.

Regression test for https://github.com/Qix-/better-exceptions/issues/87
"""
import logging
import os
import re
import sys
import tempfile

import better_exceptions

better_exceptions.hook()

ANSI_RE = re.compile(r'\x1b\[')


def _setup_file_logging(path):
    handler = logging.FileHandler(path, mode='w')
    handler.setFormatter(logging.Formatter('%(levelname)s:%(name)s:%(message)s'))
    logger = logging.getLogger('test_file_no_color')
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    return logger, handler


def test_file_handler_no_ansi():
    fd, path = tempfile.mkstemp(suffix='.log')
    os.close(fd)
    try:
        logger, handler = _setup_file_logging(path)
        try:
            raise ValueError('file logging test')
        except ValueError:
            logger.exception('caught error')
        handler.close()

        with open(path) as f:
            content = f.read()

        assert 'caught error' in content, 'log message missing'
        assert 'ValueError' in content, 'exception type missing'
        assert 'file logging test' in content, 'exception message missing'
        assert not ANSI_RE.search(content), (
            'ANSI escape codes found in file log output:\n' + content
        )
    finally:
        os.unlink(path)


if __name__ == '__main__':
    test_file_handler_no_ansi()
    print('OK: file log output contains no ANSI escape codes')
