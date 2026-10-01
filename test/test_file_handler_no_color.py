"""Regression test for #87: a FileHandler must never receive ANSI color
codes, even when a colorized stderr handler processes the exact same log
record first and caches ``record.exc_text`` (the actual leak mechanism --
see better_exceptions/log.py's _isolate_exc_text for the full explanation).
"""
from __future__ import absolute_import

import logging
import os

os.environ['FORCE_COLOR'] = '1'

import better_exceptions  # noqa: E402

better_exceptions.hook()
logging.basicConfig()  # root gets a colorized StreamHandler(stderr)

root = logging.getLogger()
LOG_PATH = 'test_file_handler_no_color.log'
file_handler = logging.FileHandler(LOG_PATH, mode='w')
root.addHandler(file_handler)

logger = logging.getLogger('test_file_handler_no_color')
logger.setLevel(logging.DEBUG)

try:
    raise ValueError('boom')
except ValueError:
    logger.exception('something broke')

file_handler.close()

with open(LOG_PATH, 'rb') as f:
    content = f.read()

os.remove(LOG_PATH)

if b'\x1b[' in content:
    print('FAIL: file handler output contains ANSI escape codes')
else:
    print('PASS: file handler output is plain text')
