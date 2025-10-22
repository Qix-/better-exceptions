"""Checks if the current terminal supports colors.

Also specifies the stream to write to. On Windows, this is a wrapped
stream.
"""

from __future__ import absolute_import

import codecs
import os
import sys


STREAM = sys.stderr
ENCODING = getattr(STREAM, "encoding", None) or "utf-8"
SHOULD_ENCODE = True
SUPPORTS_COLOR = False


def to_byte(val):
    unicode_type = str
    if isinstance(val, unicode_type):
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




class ProxyBufferStreamWrapper(object):

    def __init__(self, wrapped):
        self.__wrapped = wrapped

    def __getattr__(self, name):
        return getattr(self.__wrapped, name)

    def write(self, text):
        data = to_byte(text)
        self.__wrapped.buffer.write(data)


if os.name == 'nt':
    from colorama import init as init_colorama, AnsiToWin32

    init_colorama(wrap=False)

    stream = sys.stderr

    # Colorama cannot work with bytes-string
    # The stream is wrapped so that encoding of the stream is done after
    # (once Colorama found ANSI codes and converted them to win32 calls)
    # See issue #23 for more information
    stream = ProxyBufferStreamWrapper(stream)
    SHOULD_ENCODE = False

    STREAM = AnsiToWin32(stream).stream
    SUPPORTS_COLOR = True
else:
    if os.getenv('FORCE_COLOR', None) == '1':
        SUPPORTS_COLOR = True
    else:
        try:
            is_tty = os.isatty(2)
        except OSError:
            is_tty = False

        if is_tty:
            try:
                import curses
                curses.setupterm()
                max_colors = curses.tigetnum('colors')
                if max_colors >= 8:
                    SUPPORTS_COLOR = True
            except Exception:
                # curses.setupterm() may fail in exotic environments
                pass
