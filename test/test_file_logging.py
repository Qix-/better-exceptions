from __future__ import absolute_import

import logging
import os
import re
import sys
import tempfile

try:
    from io import StringIO
except ImportError:
    from StringIO import StringIO

import better_exceptions


ANSI_ESCAPE = re.compile(r'\x1b\[[0-9;]*m')


def fail():
    value = 52
    assert value == 90


def check_handler_order(stream_first):
    better_exceptions.SUPPORTS_COLOR = True

    logger = logging.getLogger('better_exceptions_file_logging_test_{0}'.format(stream_first))
    logger.setLevel(logging.ERROR)
    logger.propagate = False

    old_stderr = sys.stderr
    stream = StringIO()
    sys.stderr = stream
    stream_handler = logging.StreamHandler()

    fd, path = tempfile.mkstemp()
    os.close(fd)
    file_handler = logging.FileHandler(path)

    shared_formatter = logging.Formatter()
    stream_handler.setFormatter(shared_formatter)
    file_handler.setFormatter(shared_formatter)

    handlers = [stream_handler, file_handler] if stream_first else [file_handler, stream_handler]
    for handler in handlers:
        logger.addHandler(handler)

    try:
        better_exceptions.hook()
        try:
            fail()
        except AssertionError:
            logger.exception('callback failed')

        for handler in handlers:
            handler.flush()

        stream_output = stream.getvalue()
        with open(path, 'r') as log:
            file_output = log.read()

        assert ANSI_ESCAPE.search(stream_output), stream_output
        assert not ANSI_ESCAPE.search(file_output), file_output
        assert 'assert value == 90' in file_output
    finally:
        sys.stderr = old_stderr
        logger.removeHandler(stream_handler)
        logger.removeHandler(file_handler)
        stream_handler.close()
        file_handler.close()
        os.remove(path)


def main():
    check_handler_order(stream_first=True)
    check_handler_order(stream_first=False)


if __name__ == '__main__':
    main()
