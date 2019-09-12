import better_exceptions
import logging
import sys

better_exceptions.hook()
file_handler = logging.FileHandler(filename='example.log')
stream_handler = logging.StreamHandler(sys.stdout)
logging.basicConfig(level=logging.DEBUG, handlers=[file_handler, stream_handler])

logger = logging.getLogger(__name__)

logging.raiseExceptions = True

qux = 15

def foo(cb):
    qix = 20
    try:
        cb()
    except:
        logger.exception('callback failed')


def bar1():
    baz = 80.5
    logger.info('Hello')


def bar2():
    baz = 890.50
    logger.info('Hello', exc_info=True)


def bar3():
    baz = 600.524
    raise Exception('this is a test exception')


def bar4():
    baz = 52
    assert baz == 90


FNS = [
    bar1,
    bar2,
    bar3,
    bar4
]


for fn in FNS:
    foo(fn)
