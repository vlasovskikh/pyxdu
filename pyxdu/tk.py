import tkinter
from tkinter import Canvas, Tk

from pyxdu.xdu import Node, Rect, parse_file

n_cols = 5


class XduCanvas(Canvas):
    top: Node
    node: Node
    text_height: int

    def __init__(self, node: Node, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.top = node
        self.node = node
        self.bind("<Button-1>", self.on_click)
        self.text_height = self.determine_text_height()

    def draw_node(self, rect: Rect) -> None:
        self.draw_rect(self.node.name, self.node.size, rect)
        self.node.rect = rect
        sub_rect = Rect(rect.left + rect.width, rect.top, rect.width, rect.height)
        self.draw_children(self.node, sub_rect)

    def draw_children(self, node: Node, rect: Rect) -> None:
        top = rect.top

        total_size = sum(c.size for c in node.children)
        if total_size == 0:
            total_size = node.size
        if total_size == 0:
            return

        for child in node.children:
            percentage = child.size / total_size
            height = int(percentage * rect.height + 0.5)
            if height > 1:
                c_rect = Rect(rect.left, top, rect.width, height)
                self.draw_rect(child.name, child.size, c_rect)
                child.rect = c_rect

                c2_rect = Rect(rect.left + rect.width, top, rect.width, height)
                self.draw_children(child, c2_rect)

                top += height

    def draw_rect(self, name: str, size: int, rect: Rect) -> None:
        self.create_rectangle(
            rect.left, rect.top, rect.left + rect.width, rect.top + rect.height
        )

        # TODO: Ability to disable show size
        if rect.height >= self.text_height + 2:
            name = f"{name} ({size})"
            self.create_text(
                rect.left + 5, rect.top + rect.height / 2, text=name, anchor=tkinter.W
            )

    def determine_text_height(self) -> int:
        text_id = self.create_text(0, 0, text="A")
        x1, y1, x1, y2 = self.bbox(text_id)
        self.delete(text_id)
        return y2 - y1

    def repaint(self, width: int, height: int) -> None:
        rect = Rect(3, 3, int(width / n_cols) - 2, height - 2)
        self.delete("all")
        self.node.clear_rects()
        self.draw_node(rect)

    def on_click(self, event) -> None:
        n = self.node.find_node(event.x, event.y)
        if n == self.node:
            n = self.node.parent
        if n is not None:
            self.node = n
            self.repaint(800, 600)


def main_loop(filename: str) -> None:
    tk = Tk()
    tk.title("pyxdu")
    width = 800
    height = 600
    top = parse_file(filename)
    canvas = XduCanvas(top, tk, width=width, height=height)
    canvas.pack()
    canvas.repaint(height, height)

    # Hack to bring the window to the foreground
    tk.attributes("-topmost", True)
    tk.update()
    tk.attributes("-topmost", False)

    # TODO: Update on resize
    # TODO: Handle clicks
    # TODO: Handle commands

    tk.mainloop()
