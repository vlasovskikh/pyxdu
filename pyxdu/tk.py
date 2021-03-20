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

    def draw_node(self, rect: Rect) -> None:
        self.draw_rect(self.node.name, self.node.size, rect)
        self.node.rect = rect
        sub_rect = Rect(rect.left + rect.width, rect.top, rect.width, rect.height)
        self.draw_children(self.node, sub_rect, self.n_cols - 1)

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
            percentage = child.size / total_size
            height = int(percentage * rect.height + 0.5)
            if height <= 1:
                continue
            c_rect = Rect(rect.left, top, rect.width, height)
            self.draw_rect(child.name, child.size, c_rect)
            child.rect = c_rect

            c2_rect = Rect(rect.left + rect.width, top, rect.width, height)
            self.draw_children(child, c2_rect, cols - 1)

            top += height

    def draw_rect(self, name: str, size: int, rect: Rect) -> None:
        width = rect.left + rect.width
        height = rect.top + rect.height
        self.create_rectangle(rect.left, rect.top, width, height)

        # TODO: Ability to disable show size
        if rect.height >= self.text_height + 2:
            x = rect.left + 5
            y = rect.top + rect.height / 2
            self.create_text(x, y, text=f"{name} ({size})", anchor=tkinter.W)

    def determine_text_height(self) -> int:
        text_id = self.create_text(0, 0, text="A")
        x1, y1, x1, y2 = self.bbox(text_id)
        self.delete(text_id)
        return y2 - y1

    def repaint(self) -> None:
        rect = Rect(3, 3, int(self.width / self.n_cols) - 2, self.height - 2)
        self.delete("all")
        self.node.clear_rects()
        self.draw_node(rect)

    def on_click(self, event: Any) -> None:
        n = self.node.find_node(event.x, event.y)
        if n == self.node:
            n = self.node.parent
        if n is not None:
            self.node = n
            self.repaint()


def main_loop(filename: str, order: Order) -> None:
    tk = tkinter.Tk()
    tk.title("pyxdu")
    top = parse_file(filename)
    if order != Order.DEFAULT:
        top.sort_tree(order)
    canvas = XduCanvas(tk, top, width=800, height=600)
    canvas.pack()
    canvas.repaint()

    # Hack to bring the window to the foreground
    tk.attributes("-topmost", True)
    tk.update()
    tk.attributes("-topmost", False)

    # TODO: Update on resize
    # TODO: Handle commands

    tk.mainloop()
