from distutils.core import setup

VERSION = '0.1.5'

setup(
    name = 'better_exceptions',
    packages = ['better_exceptions'],
    version = VERSION,
    description = 'Pretty and helpful exceptions, automatically',
    author = 'Josh Junon',
    author_email = 'josh@junon.me',
    url = 'https://github.com/qix-/better-exceptions',
    download_url = 'https://github.com/qix-/better-exceptions/archive/{}.tar.gz'.format(VERSION),
    keywords = ['pretty', 'better', 'exceptions', 'exception', 'error', 'local', 'debug', 'debugging', 'locals'],
    classifiers = [],
    extras_require = {
        ':sys_platform=="win32"': ['colorama']
    }
)
