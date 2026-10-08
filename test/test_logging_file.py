from __future__ import absolute_import

import logging
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import better_exceptions


ANSI_ESCAPE = '\x1b['


def explode():
    marker = 'file logs should not be colorized'
    raise RuntimeError(marker)


def main():
    path = os.path.join(tempfile.gettempdir(), 'better_exceptions_file_logging.log')
    try:
        os.remove(path)
    except OSError:
        pass

    logger = logging.getLogger('better_exceptions.file_logging')
    logger.handlers[:] = []
    logger.propagate = False
    logger.setLevel(logging.ERROR)

    formatter = logging.Formatter('%(levelname)s:%(message)s')

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(path, mode='w')
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    better_exceptions.hook()

    try:
        explode()
    except RuntimeError:
        logger.exception('shared formatter failure')

    file_handler.close()

    with open(path, 'r') as logfile:
        logged = logfile.read()

    assert ANSI_ESCAPE not in logged, logged


if __name__ == '__main__':
    main()
