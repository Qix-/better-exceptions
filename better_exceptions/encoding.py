from __future__ import absolute_import

import codecs
import locale
import sys


ENCODING = locale.getpreferredencoding()


def to_byte(val):
    if isinstance(val, str):
        try:
            return val.encode(ENCODING)
        except UnicodeEncodeError:
            return codecs.escape_decode(val)[0]

    return val


def to_unicode(val):
    if isinstance(val, bytes):
        try:
            return val.decode(ENCODING)
        except UnicodeDecodeError:
            return val.decode("unicode-escape")

    return val
