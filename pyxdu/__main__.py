"""pyxdu - Display the output of "du" in a window.

Usage: pyxdu [options] <file>
       pyxdu [options] [-]
       pyxdu --help

Options:
    -h --help       Show this message.
    -n              Sort in numerical order.
    --dump <file>   Dump tree as JSON for debugging.
"""

import docopt
import os
import sys
from typing import List

from pyxdu.tk import main_loop
from pyxdu.xdu import Order, parse_file


def main(argv: List[str]) -> None:
    order = Order.DEFAULT
    opts = docopt.docopt(__doc__, argv)

    if opts["<file>"] in ("-", None):
        if os.isatty(sys.stdin.fileno()):
            print(docopt.printable_usage(__doc__), file=sys.stderr)
            sys.exit(1)
        else:
            filename = "-"
    else:
        filename = opts["<file>"]

    if opts["-n"]:
        order = Order.SIZE

    dump_file = opts["--dump"]
    if dump_file:
        top = parse_file(filename)
        if order != Order.DEFAULT:
            top.sort_tree(order)
        with open(dump_file, "w") as fd:
            fd.write(top.dump_tree())
    else:
        main_loop(filename, order)


def run() -> None:
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        print("Interrupted")


if __name__ == "__main__":
    run()
