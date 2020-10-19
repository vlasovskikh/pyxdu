import tkinter
from tkinter import Canvas, Tk

from pyxdu.xdu import Node, Rect, parse_file

n_cols = 5


class XduCanvas(Canvas):
    node: Node

    def __init__(self, node: Node, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.node = node

    def draw_node(self, rect: Rect) -> None:
        self.draw_rect(self.node.name, self.node.size, rect)
        self.node.rect = rect
        sub_rect = Rect(rect.left + rect.width, rect.top, rect.width,
                        rect.height)
        self.draw_children(self.node, sub_rect)

    def draw_children(self, node: Node, rect: Rect) -> None:
        # if node.size == 0:
        #     node.size = sum((c.size for c in node.children))
        top = rect.top
        total_size = node.size

        for child in node.children:
            size = child.size / total_size
            height = int(size * rect.height + 0.5)
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
        name = f"{name} ({size})"
        self.create_text(rect.left, rect.top, text=name)

    def repaint(self, width: int, height: int) -> None:
        rect = Rect(0, 0, int(width / n_cols), height)
        self.node.clear_rects()
        self.draw_node(rect)


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
    tk.attributes('-topmost', True)
    tk.update()
    tk.attributes('-topmost', False)

    # TODO: Update on resize
    # TODO: Handle clicks
    # TODO: Handle commands

    tk.mainloop()
