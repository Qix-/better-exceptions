"""Checks if the current terminal supports colors.

Also specifies the stream to write to. On Windows, this is a wrapped
stream.
"""

from __future__ import absolute_import

import errno
import os
import struct
import sys

from .context import PY3
from .encoding import to_byte as _byte


STREAM = sys.stderr
SHOULD_ENCODE = True
SUPPORTS_COLOR = False


def get_terminfo_file():
    term = os.getenv('TERM', None)

    if term is None:
        return None

    terminfo_dirs = [
            os.path.expanduser('~/.terminfo'),
            '/etc/terminfo',
            '/lib/terminfo',
            '/usr/share/terminfo',
            '/usr/lib/terminfo',
            '/usr/share/lib/terminfo',
            '/usr/local/lib/terminfo',
            '/usr/local/share/terminfo'
            ]

    subdirs = [
            ('%0.2X' % ord(term[0])),
            term[0]
            ]

    f = None
    for terminfo_dir in terminfo_dirs:
        for subdir in subdirs:
            terminfo_path = os.path.join(terminfo_dir, subdir, term)
            try:
                f = open(terminfo_path, 'rb')
                break
            except IOError as e:
                if e.errno != errno.ENOENT:
                    raise

    return f


class ProxyBufferStreamWrapper(object):

    def __init__(self, wrapped):
        self.__wrapped = wrapped

    def __getattr__(self, name):
        return getattr(self.__wrapped, name)

    def write(self, text):
        data = _byte(text)
        self.__wrapped.buffer.write(data)


if os.name == 'nt':
    from colorama import init as init_colorama, AnsiToWin32

    init_colorama(wrap=False)

    stream = sys.stderr

    if PY3:
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
            # May raises an error on some exotic environment like GAE, see #28
            is_tty = os.isatty(2)
        except OSError:
            is_tty = False

        if is_tty:
            f = get_terminfo_file()
            if f is not None:
                with f:
                    # f is a valid terminfo; seek and read!
                    magic_number = struct.unpack('<h', f.read(2))[0]

                    if magic_number == 0x11A:
                        # the opened terminfo file is valid.
                        offset = 2 + 10  # magic number + size section (the next thing we read from)
                        offset += struct.unpack('<h', f.read(2))[0]  # skip over names section
                        offset += struct.unpack('<h', f.read(2))[0]  # skip over bool section
                        offset += offset % 2  # align to short boundary
                        offset += 13 * 2  # maxColors is the 13th numeric value

                        f.seek(offset)
                        max_colors = struct.unpack('<h', f.read(2))[0]

                        if max_colors >= 8:
                            SUPPORTS_COLOR = True
