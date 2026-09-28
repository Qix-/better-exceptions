"""Logged exceptions must not contain ANSI color codes (IssueHunt #87)."""
from __future__ import absolute_import

import logging
import os
import re
import tempfile

import better_exceptions

ANSI_ESCAPE = re.compile(r'\x1b\[[0-9;]*m')


def main():
    # Force color support on so we can prove logging still strips it.
    better_exceptions.SUPPORTS_COLOR = True
    better_exceptions.hook()

    fd, path = tempfile.mkstemp(suffix='.log')
    os.close(fd)

    logger = logging.getLogger('better_exceptions.issue87')
    logger.handlers = []
    logger.propagate = False
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(path)
    file_handler.setFormatter(logging.Formatter('%(message)s'))
    logger.addHandler(file_handler)

    # Re-run patch after handlers exist so formatException is applied.
    better_exceptions.log.patch()

    try:
        raise RuntimeError('colour-in-logs regression')
    except Exception:
        logger.exception('logged failure')

    file_handler.close()
    with open(path, 'r') as handle:
        content = handle.read()
    os.unlink(path)

    assert 'colour-in-logs regression' in content or 'RuntimeError' in content, content
    assert ANSI_ESCAPE.search(content) is None, 'ANSI color codes found in log file:\n%s' % content
    print('ok')


if __name__ == '__main__':
    main()
