from code import InteractiveConsole
import sys


REPL_ID_PREFIX = '@@@REPL@@@'


repl = None

class BetterExceptionsConsole(InteractiveConsole, object):
    def __init__(self):
        super(BetterExceptionsConsole, self).__init__()
        self.last_command = None
        self.entries = dict()
        self.last_code = None
        self.last_id = None
        self.counter = 0

    def runcode(self, code):
        assert self.last_code is not None
        self.entries[self.last_id] = (code,) + self.last_code
        return super(BetterExceptionsConsole, self).runcode(code)

    def runsource(self, source, loc='<input>', symbol='single'):
        # we abuse loc here to mark different entries of code.
        self.last_code = (loc, source)
        self.last_id = loc = '{}{}'.format(REPL_ID_PREFIX, self.counter)
        self.counter += 1
        return super(BetterExceptionsConsole, self).runsource(source, loc, symbol)

    def showtraceback(self):
        try:
            exctype, val, tb = sys.exc_info()
            sys.excepthook(exctype, val, tb)
        finally:
            # this is required since tb will never be garbage collected
            # see notes in `sys`
            del tb


def get_repl():
    global repl
    return repl


def interact(quiet=False):
    global repl
    repl = BetterExceptionsConsole()
    banner = '' if quiet else None
    repl.interact(banner)
