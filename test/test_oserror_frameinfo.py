# -*- coding:utf-8 -*-

import inspect
import sys

from better_exceptions.formatter import ExceptionFormatter


def _raise_oserror(tb, *args, **kwargs):
    raise FileNotFoundError(2, 'No such file or directory')


def main():
    original = inspect.getframeinfo
    inspect.getframeinfo = _raise_oserror
    try:
        try:
            raise ValueError('boom')
        except ValueError:
            exc_type, exc_value, exc_tb = sys.exc_info()
            formatted = ''.join(
                ExceptionFormatter().format_exception(exc_type, exc_value, exc_tb)
            )
    finally:
        inspect.getframeinfo = original

    assert 'ValueError: boom' in formatted, formatted
    assert 'Traceback (most recent call last):' in formatted, formatted


if __name__ == '__main__':
    main()
