import logging
import os
import tempfile

import better_exceptions


better_exceptions.hook()


def make_logger(log_path):
    logger = logging.getLogger('test_file_handler')
    logger.handlers = []
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler(log_path)
    file_handler.setFormatter(logging.Formatter('%(levelname)s:%(message)s'))
    logger.addHandler(file_handler)
    return logger


fd, path = tempfile.mkstemp(prefix='better-exceptions-', suffix='.log')
os.close(fd)

logger = make_logger(path)

try:
    raise RuntimeError('boom')
except RuntimeError:
    logger.exception('captured')

with open(path, 'r') as f:
    content = f.read()

assert '\x1b[' not in content, content
print('ok')
