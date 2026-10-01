"""Edge-case regression tests for _isolate_exc_text (see log.py), raised
during review of the #87 fix:

1. A pre-existing (non-empty) record.exc_text must be PRESERVED, not
   unconditionally wiped -- some other, unrelated code may have legitimately
   set it before any handler ran.
2. record.exc_text must be restored even if the wrapped format() call
   itself raises -- otherwise a mid-formatting exception leaves a stale
   (possibly colorized) value cached and ready to leak into the next
   handler, exactly like the bug this is fixing.
"""
from __future__ import absolute_import

import logging

from better_exceptions.log import _isolate_exc_text


def _case_1_preserve_pre_existing_value():
    fmt = logging.Formatter('%(message)s')
    _isolate_exc_text(fmt)

    record = logging.LogRecord('x', logging.ERROR, __file__, 1, 'msg', None, None)
    record.exc_text = 'PRE-EXISTING SENTINEL VALUE'
    fmt.format(record)

    if record.exc_text == 'PRE-EXISTING SENTINEL VALUE':
        print('PASS: pre-existing exc_text was preserved')
    else:
        print('FAIL: pre-existing exc_text was not preserved, got %r' % (record.exc_text,))


def _case_2_restore_survives_exception():
    fmt = logging.Formatter('%(message)s')

    def exploding_format(record):
        raise RuntimeError('simulated formatting failure')

    fmt.format = exploding_format
    _isolate_exc_text(fmt)

    record = logging.LogRecord('x', logging.ERROR, __file__, 1, 'msg', None, None)
    record.exc_text = 'SHOULD SURVIVE AN EXCEPTION'
    try:
        fmt.format(record)
        print('FAIL: expected RuntimeError to propagate')
    except RuntimeError:
        if record.exc_text == 'SHOULD SURVIVE AN EXCEPTION':
            print('PASS: exc_text was restored despite the exception')
        else:
            print('FAIL: exc_text was not restored, got %r' % (record.exc_text,))


_case_1_preserve_pre_existing_value()
_case_2_restore_survives_exception()
