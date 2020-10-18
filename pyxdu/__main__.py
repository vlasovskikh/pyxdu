"""pyxdu - Display the output of "du" in a window.

Usage: pyxdu [options] <filename>
       pyxdu [options] [-]
       pyxdu --help

Options:
    -h --help       Show this message.
    --dump          Dump tree as JSON for debugging.
"""

import logging
import os
import sys
from logging import debug
from typing import List

import docopt

from pyxdu.tk import main_loop
from pyxdu.xdu import Order, parse_file


def main(argv: List[str]) -> None:
    order = Order.DEFAULT
    opts = docopt.docopt(__doc__, argv)

    debug("xsetup(...)")
    if opts["<filename>"] in ("-", None):
        if os.isatty(sys.stdin.fileno()):
            print(docopt.printable_usage(__doc__), file=sys.stderr)
            sys.exit(1)
        else:
            top = parse_file("-")
    else:
        top = parse_file(opts["<filename>"])

    if order != Order.DEFAULT:
        debug("sort_tree(top, order)")

    # don't display root if only one child
    if len(top.children) == 1:
        top = top.children[0]

    if opts["--dump"]:
        print(top.dump_tree())
    else:
        main_loop(top)


def run() -> None:
    logging.basicConfig(level=logging.DEBUG)
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        print("Interrupted")


if __name__ == "__main__":
    run()
