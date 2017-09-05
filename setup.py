import re
from distutils.core import setup

with open('better_exceptions/__init__.py', 'r') as file:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        file.read(), re.MULTILINE).group(1)

setup(
    name = 'better_exceptions',
    packages = ['better_exceptions'],
    version = version,
    description = 'Pretty and helpful exceptions, automatically',
    author = 'Josh Junon',
    author_email = 'josh@junon.me',
    url = 'https://github.com/qix-/better-exceptions',
    download_url = 'https://github.com/qix-/better-exceptions/archive/{}.tar.gz'.format(version),
    keywords = ['pretty', 'better', 'exceptions', 'exception', 'error', 'local', 'debug', 'debugging', 'locals'],
    classifiers = [],
    extras_require = {
        ':sys_platform=="win32"': ['colorama']
    }
)
