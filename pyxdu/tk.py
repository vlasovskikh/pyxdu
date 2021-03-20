import tkinter
from typing import Any

from pyxdu.xdu import Node, Rect, parse_file, Order


class XduCanvas(tkinter.Canvas):
    top: Node
    node: Node
    width: int
    height: int
    n_cols: int
    text_height: int

    def __init__(
        self, parent: tkinter.Misc, node: Node, width: int, height: int
    ) -> None:
        super().__init__(parent, width=width, height=height)
        self.top = node
        self.node = node
        self.width = width
        self.height = height
        self.n_cols = 5
        self.text_height = self.determine_text_height()
        self.bind("<Button-1>", self.on_click)
        self.bind("<Configure>", self.on_resize)

    def draw_node_and_children(self, rect: Rect) -> None:
        self.node.rect = rect
        self.draw_node(self.node)
        c_rect = Rect(rect.left + rect.width, rect.top, rect.width, rect.height)
        self.draw_children(self.node, c_rect, self.n_cols - 1)

    def draw_children(self, node: Node, rect: Rect, cols: int) -> None:
        if cols <= 0:
            return

        total_size = sum(c.size for c in node.children)
        if total_size == 0:
            total_size = node.size
        if total_size == 0:
            return

        top = rect.top
        for child in node.children:
            top += self.draw_child(child, rect, top, total_size, cols)

    def draw_child(
        self, node: Node, parent_rect: Rect, top: int, total_size: int, cols: int
    ) -> int:
        percentage = node.size / total_size
        height = int(percentage * parent_rect.height + 0.5)
        if height <= 1:
            return 0
        node.rect = Rect(parent_rect.left, top, parent_rect.width, height)
        self.draw_node(node)

        c_left = parent_rect.left + parent_rect.width
        c_rect = Rect(c_left, top, parent_rect.width, height)
        self.draw_children(node, c_rect, cols - 1)

        return height

    def draw_node(self, node: Node) -> None:
        rect = node.rect
        width = rect.left + rect.width
        height = rect.top + rect.height
        self.create_rectangle(rect.left, rect.top, width, height)

        # TODO: Ability to disable show size
        if rect.height >= self.text_height + 2:
            self.create_text(
                rect.left + 5,
                rect.top + rect.height / 2,
                text=f"{node.name} ({node.size})",
                anchor=tkinter.W,
            )

    def determine_text_height(self) -> int:
        text_id = self.create_text(0, 0, text="A")
        x1, y1, x1, y2 = self.bbox(text_id)
        self.delete(text_id)
        return y2 - y1

    def repaint(self) -> None:
        rect = Rect(3, 3, int(self.width / self.n_cols) - 2, self.height - 2)
        self.delete("all")
        self.node.clear_rects()
        self.draw_node_and_children(rect)

    def on_click(self, event: Any) -> None:
        n = self.node.find_node(event.x, event.y)
        if n == self.node:
            n = self.node.parent
        if n is not None:
            self.node = n
            self.repaint()

    def on_resize(self, event: Any) -> None:
        w_scale = event.width / self.width
        h_scale = event.height / self.height
        self.scale("all", 0, 0, w_scale, h_scale)
        self.width = event.width
        self.height = event.height


def main_loop(filename: str, order: Order) -> None:
    tk = tkinter.Tk()
    tk.title("pyxdu")
    top = parse_file(filename)
    if order != Order.DEFAULT:
        top.sort_tree(order)
    canvas = XduCanvas(tk, top, width=800, height=600)
    canvas.pack(fill="both", expand=True)
    canvas.repaint()

    # Hack to bring the window to the foreground
    tk.attributes("-topmost", True)
    tk.update()
    tk.attributes("-topmost", False)

    # TODO: Handle commands

    tk.mainloop()
