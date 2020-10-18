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

    if opts["<filename>"] in ("-", None):
        if os.isatty(sys.stdin.fileno()):
            print(docopt.printable_usage(__doc__), file=sys.stderr)
            sys.exit(1)
        else:
            filename = "-"
    else:
        filename = opts["<filename>"]

    if order != Order.DEFAULT:
        debug("sort_tree(top, order)")

    if opts["--dump"]:
        top = parse_file(filename)
        print(top.dump_tree())
    else:
        main_loop(filename)


def run() -> None:
    logging.basicConfig(level=logging.DEBUG)
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        print("Interrupted")


if __name__ == "__main__":
    run()
