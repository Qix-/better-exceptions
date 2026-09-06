import sys
import re

def strip_ansi(text):
    ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
    return ansi_escape.sub('', text)

def write_to_stream(stream, text):
    if hasattr(stream, "isatty") and not stream.isatty():
        text = strip_ansi(text)
    stream.write(text)
