from __future__ import absolute_import

import io
import logging
import os
import re
import sys
import tempfile

import better_exceptions


ANSI_ESCAPE = re.compile(r'\x1b\[[0-9;]*m')


def raise_exception():
    value = 52
    assert value == 90


def main():
    better_exceptions.SUPPORTS_COLOR = True
    better_exceptions.hook()

    fd, path = tempfile.mkstemp()
    os.close(fd)

    original_stderr = sys.stderr
    terminal = io.StringIO()
    root = logging.getLogger()

    try:
        sys.stderr = terminal
        file_handler = logging.FileHandler(path)
        stream_handler = logging.StreamHandler(sys.stderr)
        logging.basicConfig(level=logging.DEBUG, handlers=[file_handler, stream_handler])

        logger = logging.getLogger(__name__)
        try:
            raise_exception()
        except AssertionError:
            logger.exception('callback failed')

        for handler in root.handlers:
            handler.flush()

        with open(path) as log_file:
            file_output = log_file.read()

        terminal_output = terminal.getvalue()
        assert ANSI_ESCAPE.search(terminal_output), terminal_output
        assert not ANSI_ESCAPE.search(file_output), file_output
    finally:
        sys.stderr = original_stderr
        for handler in root.handlers[:]:
            handler.close()
            root.removeHandler(handler)
        os.remove(path)


if __name__ == '__main__':
    main()
