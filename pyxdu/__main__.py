"""pyxdu - Display the output of "du" in a window.

Usage: pyxdu [options] <file>
       pyxdu [options] [-]
       pyxdu --help

Options:
    -h --help      Show this message.
    -a             Sort in alphabetical order.
    -n             Sort in numerical order (the largest first).
    -r             Reverse sense of sort (e.g. -rn means the smallest first).
    -c <num>       Display <num> columns [default: 6].
    --dump <file>  Dump tree as JSON for debugging.

Keystrokes:
    1-9,0      Sets the number of columns in the display (0 = 10).
    a          Alphabetical sort.
    n          Numerical sort (the largest first).
    f          First-in-first-out sort (this is the order the data was read
                                        into the program).
    l          Last-in-first-out sort.
    r          Reverse sense of sort.
    /          Goto the root.
    q, Escape  Exit the program.

See also the documentation at https://github.com/vlasovskikh/pyxdu
"""

import docopt
import os
import sys
from typing import List, Dict, Any

from pyxdu.tk import main_loop
from pyxdu.xdu import Order, parse_file, error


def main(argv: List[str]) -> None:
    opts = docopt.docopt(__doc__, argv)

    if opts["<file>"] in ("-", None):
        if os.isatty(sys.stdin.fileno()):
            print(docopt.printable_usage(__doc__), file=sys.stderr)
            sys.exit(1)
        else:
            filename = "-"
    else:
        filename = opts["<file>"]

    order = parse_order(opts)

    try:
        columns = int(opts["-c"])
    except ValueError:
        error("Columns count must be integer")
        sys.exit(1)

    # TODO: Handle more CLI options: -s, --background <color>, --foreground <color>

    dump_file = opts["--dump"]
    if dump_file:
        top = parse_file(filename)
        if order != Order.DEFAULT:
            top.sort_tree(order)
        with open(dump_file, "w") as fd:
            fd.write(top.dump_tree())
    else:
        main_loop(filename, order=order, columns=columns)


def parse_order(opts: Dict[str, Any]) -> Order:
    if opts["-a"]:
        order = Order.ALPHA
    elif opts["-n"]:
        order = Order.SIZE
    else:
        order = Order.DEFAULT

    return -order if opts["-r"] else order


def run() -> None:
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        print("Interrupted")


if __name__ == "__main__":
    run()
