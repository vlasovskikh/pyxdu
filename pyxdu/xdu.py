from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

import json
import os
import sys
from typing import List, ClassVar, Optional, TextIO, Dict, Union, Any

__all__ = ["Rect", "Order", "Node", "parse_file", "parse_fd", "error"]


class Order(Enum):
    FIRST = DEFAULT = auto()
    LAST = auto()
    ALPHA = auto()
    SIZE = auto()
    R_ALPHA = auto()
    R_SIZE = auto()

    def sort_key(self, node: Node) -> Any:
        if self == Order.SIZE or self == Order.R_SIZE:
            return node.size
        elif self == Order.ALPHA or self == Order.R_ALPHA:
            return node.name
        else:
            return node.num

    @property
    def reverse(self) -> bool:
        return self in {Order.LAST, Order.R_ALPHA, Order.SIZE}

    def __neg__(self) -> Order:
        return reversed_orders[self]


reversed_orders: Dict[Order, Order] = {
    Order.FIRST: Order.LAST,
    Order.ALPHA: Order.R_ALPHA,
    Order.SIZE: Order.R_SIZE,
}
reversed_orders.update({v: k for k, v in reversed_orders.items()})


@dataclass
class Rect:
    """Rectangle Structure

    Stores window coordinates of a displayed rectangle
    so that we can "find" it again on key presses.
    """

    left: int
    top: int
    width: int
    height: int


class Node:
    """Node Structure

    Each node in the path tree is linked in with one of these.
    """

    name: str
    size: int  # from here down in the tree
    num: int  # entry number - for resorting
    rect: Rect  # last drawn screen rectangle
    children: List[Node]  # list of children
    children_by_name: Dict[str, Node]  # cache children by name
    parent: Optional[Node]  # back-pointer to parent

    n_nodes: ClassVar[int] = 0

    def __init__(self, name: str, size: int) -> None:
        """Create a new node with the given name and size info."""
        self.name = name
        self.size = size
        self.num = Node.n_nodes
        self.rect = Rect(0, 0, 0, 0)
        self.children = []
        self.children_by_name = {}
        self.parent = None
        Node.n_nodes += 1

    def find_node(self, x: int, y: int) -> Optional[Node]:
        """Return the node (if any) which has a draw rectangle containing
        the given x,y point.
        """
        if (
            self.rect.left <= x < self.rect.left + self.rect.width
            and self.rect.top <= y < self.rect.top + self.rect.height
        ):
            return self

        found = (c.find_node(x, y) for c in self.children)
        return next(filter(None, found), None)

    def fix_tree(self) -> int:
        """This function repairs the tree when certain nodes haven't
        had their sizes initialized. [DPT911113]
        """
        children_size = sum(c.fix_tree() for c in self.children)
        if self.size < 0:
            self.size = children_size
        return self.size

    def add_tree(self, path: List[str], size: int) -> None:
        """Add a path as a child - recursively."""
        first, *rest = path
        child = self.children_by_name.get(first)

        if child is None:
            child = Node(first, -1)
            self.insert_child(child)

        if len(rest) == 0:
            child.size = size
        else:
            child.add_tree(rest, size)

    def insert_child(self, child: Node) -> None:
        child.parent = self
        self.children.append(child)
        self.children_by_name[child.name] = child

    def __repr__(self) -> str:
        return f"<Node: {self.name}, {self.size}, children=" f"{len(self.children)}>"

    def clear_rects(self) -> None:
        self.rect = Rect(0, 0, 0, 0)
        for child in self.children:
            child.clear_rects()

    def to_json(self) -> dict:
        return {
            "name": self.name,
            "size": self.size,
            "children": [c.to_json() for c in self.children],
        }

    def dump_tree(self) -> str:
        return json.dumps(self.to_json(), ensure_ascii=False)

    def sort_tree(self, order: Order) -> None:
        for child in self.children:
            child.sort_tree(order)
        self.children.sort(key=order.sort_key, reverse=order.reverse)


def parse_file(filename: str) -> Node:
    fn: Union[int, str] = sys.stdin.fileno() if filename == "-" else filename
    with open(fn, "r") as file:
        return parse_fd(file)


def parse_fd(fd: TextIO) -> Node:
    top = Node("[root]", -1)
    for line in fd:
        try:
            size_str, name = line.strip().split(None, 1)
            size = int(size_str)
        except ValueError:
            error(f"Skipping: {line.strip()}")
            continue
        parts = name.split(os.sep)
        if len(parts) > 0:
            if parts[0] == "":
                parts[0] = "/"
            parts = [part for part in parts if part != "" and part != "."]
            if len(parts) > 0:
                top.add_tree(parts, size)

    # don't display root if only one child
    if len(top.children) == 1:
        top = top.children[0]
        top.parent = None

    top.fix_tree()

    return top


def error(message: str) -> None:
    print(f"pyxdu: {message}", file=sys.stderr)
