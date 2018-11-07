from __future__ import absolute_import

import codecs
import locale
import sys

from .context import PY3


ENCODING = locale.getpreferredencoding()


def to_byte(val):
    unicode_type = str if PY3 else unicode
    if isinstance(val, unicode_type):
        try:
            return val.encode(ENCODING)
        except UnicodeEncodeError:
            if PY3:
                return codecs.escape_decode(val)[0]
            else:
                return val.encode("unicode-escape").decode("string-escape")

    return val


def to_unicode(val):
    if isinstance(val, bytes):
        try:
            return val.decode(ENCODING)
        except UnicodeDecodeError:
            return val.decode("unicode-escape")

    return val
