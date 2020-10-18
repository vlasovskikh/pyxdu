from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from enum import Enum, auto
from functools import total_ordering
from pathlib import PurePath
from typing import List, ClassVar, Optional, TextIO

__all__ = ["Rect", "Order", "Node", "parse_file", "parse_fd"]


class Order(Enum):
    FIRST = DEFAULT = auto()
    LAST = auto()
    ALPHA = auto()
    SIZE = auto()
    R_ALPHA = auto()
    R_SIZE = auto()


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


@total_ordering
class Node:
    """Node Structure

    Each node in the path tree is linked in with one of these.
    """

    name: str
    size: int  # from here down in the tree
    num: int  # entry number - for resorting
    rect: Rect  # last drawn screen rectangle
    children: List[Node]  # list of children
    parent: Optional[Node]  # back-pointer to parent

    n_nodes: ClassVar[int] = 0

    def __init__(self, name: str, size: int) -> None:
        """Create a new node with the given name and size info."""
        self.name = name
        self.size = size
        self.num = self.n_nodes
        self.rect = Rect(0, 0, 0, 0)
        self.children = []
        self.parent = None
        self.n_nodes += 1

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
        child = next((c for c in self.children if c.name == first), None)

        if child is None:
            child = Node(first, -1)
            self.insert_child(child)

        if len(rest) == 0:
            child.size = size
        else:
            child.add_tree(rest, size)

    def insert_child(self, child: Node) -> None:
        child.parent = self
        ge = next((c for c in self.children if child < c), None)

        if ge is None:
            self.children.append(child)
        else:
            self.children.insert(self.children.index(ge), child)

    def __eq__(self, other: Node) -> bool:
        # TODO: Add non-default orders
        return self.num == other.num

    def __le__(self, other: Node) -> bool:
        # TODO: Add non-default orders
        return self.num < other.num

    def __repr__(self) -> str:
        return f'<Node: {self.name}, {self.size}, children=' \
               f'{len(self.children)}>'

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
        return json.dumps(self.to_json(), ensure_ascii=False, indent=4)


def parse_file(filename: str) -> Node:
    fn = sys.stdin.fileno() if filename == "-" else filename
    with open(fn, "r") as file:
        return parse_fd(file)


def parse_fd(fd: TextIO) -> Node:
    top = Node("[root]", -1)
    for line in fd:
        size, name = re.split(r"\s+", line.strip(), 1)
        size = int(size)
        parts = list(PurePath(name).parts)
        if len(parts) > 0:
            top.add_tree(parts, size)

    # don't display root if only one child
    if len(top.children) == 1:
        top = top.children[0]

    top.fix_tree()

    return top
