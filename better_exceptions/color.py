"""Checks if the current terminal supports colors.

Also specifies the stream to write to. On Windows, this is a wrapped
stream.
"""

import errno
import os
import struct
import sys


STREAM = sys.stderr
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


if os.name == 'nt':
    from colorama import init as init_colorama, AnsiToWin32

    init_colorama(wrap=False)
    STREAM = AnsiToWin32(sys.stderr).stream
    SUPPORTS_COLOR = True
else:
    if os.getenv('FORCE_COLOR', None) == '1':
        SUPPORTS_COLOR = True
    elif os.isatty(2):
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
