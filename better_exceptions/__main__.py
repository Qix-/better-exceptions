import argparse
import imp
import os

from better_exceptions import interact

parser = argparse.ArgumentParser(description='A Python REPL with better exceptions enabled', prog='python -m better_exceptions')
parser.add_argument('-q', '--quiet', help="don't show a banner", action='store_true')
parser.add_argument('-i', '--no-init', dest='no_init', help="don't load ~/.pyinit", action='store_true')
args = parser.parse_args()

startup_file = os.getenv('PYTHONSTARTUP')
if not args.no_init and startup_file is not None:
    with open(startup_file, 'r') as fd:
        imp.load_module('pystartup', fd, startup_file, ('.py', 'r', imp.PY_SOURCE))

interact(args.quiet)
