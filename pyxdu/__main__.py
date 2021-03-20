"""pyxdu - Display the output of "du" in a window.

Usage: pyxdu [options] <file>
       pyxdu [options] [-]
       pyxdu --help

Options:
    -h --help           Show this message.
    -n                  Sort in numerical order.
    -c --columns <num>  Display <num> columns [default: 6].
    --dump <file>       Dump tree as JSON for debugging.

Keystrokes:
    1-9,0       Sets the number of columns in the display (0 = 10).
    /           Goto the root.
"""

import docopt
import os
import sys
from typing import List

from pyxdu.tk import main_loop
from pyxdu.xdu import Order, parse_file, error


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

    try:
        columns = int(opts["--columns"])
    except ValueError:
        error("Columns count must be integer")
        sys.exit(1)

    dump_file = opts["--dump"]
    if dump_file:
        top = parse_file(filename)
        if order != Order.DEFAULT:
            top.sort_tree(order)
        with open(dump_file, "w") as fd:
            fd.write(top.dump_tree())
    else:
        main_loop(filename, order=order, columns=columns)


def run() -> None:
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        print("Interrupted")


if __name__ == "__main__":
    run()
