import argparse

from better_exceptions import interact

parser = argparse.ArgumentParser(description='A Python REPL with better exceptions enabled', prog='python -m better_exceptions')
parser.add_argument('-q', '--quiet', help="don't show a banner", action='store_true')
args = parser.parse_args()

interact(args.quiet)
