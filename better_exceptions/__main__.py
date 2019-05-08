import argparse
import os

try:
    import importlib.machinery
    import importlib.util

    def load_module(name, filepath):
        loader = importlib.machinery.SourceFileLoader(name, filepath)
        spec = importlib.util.spec_from_loader(loader.name, loader)
        mod = importlib.util.module_from_spec(spec)
        loader.exec_module(mod)

except ImportError:
    import imp

    def load_module(name, filepath):
        with open(filepath, 'r') as fd:
            imp.load_module('a_b', fd, filepath, ('.py', 'U', imp.PY_SOURCE))

from better_exceptions import interact, hook
hook()

parser = argparse.ArgumentParser(description='A Python REPL with better exceptions enabled', prog='python -m better_exceptions')
parser.add_argument('-q', '--quiet', help="don't show a banner", action='store_true')
parser.add_argument('-i', '--no-init', dest='no_init', help="don't load ~/.pyinit", action='store_true')
args = parser.parse_args()

startup_file = os.getenv('PYTHONSTARTUP')
if not args.no_init and startup_file is not None:
    load_module('pystartup', startup_file)

interact(args.quiet)
