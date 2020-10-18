from tkinter import Canvas, Tk

from pyxdu.xdu import Node, Rect, parse_file

n_cols = 5


def draw_node(canvas: Canvas, node: Node, rect: Rect) -> None:
    draw_rect(canvas, node.name, node.size, rect)
    node.rect = rect
    sub_rect = Rect(rect.left + rect.width, rect.top, rect.width, rect.height)
    draw_children(canvas, node, sub_rect)


def draw_children(canvas: Canvas, node: Node, rect: Rect) -> None:
    # if node.size == 0:
    #     node.size = sum((c.size for c in node.children))
    top = rect.top
    total_size = node.size

    for child in node.children:
        size = child.size / total_size
        height = int(size * rect.height + 0.5)
        if height > 1:
            c_rect = Rect(rect.left, top, rect.width, height)
            draw_rect(canvas, child.name, child.size, c_rect)
            child.rect = c_rect

            c2_rect = Rect(rect.left + rect.width, top, rect.width, height)
            draw_children(canvas, child, c2_rect)

            top += height


def draw_rect(canvas: Canvas, name: str, size: int, rect: Rect) -> None:
    canvas.create_rectangle(rect.left, rect.top, rect.width, rect.height)

    # TODO: Ability to disable show size
    name = f"{name} ({size})"
    canvas.create_text(rect.left, rect.top, text=name)


def repaint(canvas: Canvas, node: Node, width: int, height: int) -> None:
    rect = Rect(0, 0, int(width / n_cols), height)
    node.clear_rects()
    draw_node(canvas, node, rect)


def main_loop(filename: str) -> None:
    tk = Tk()
    tk.title("pyxdu")
    width = 800
    height = 600
    canvas = Canvas(tk, width=width, height=height)
    canvas.pack()
    top = parse_file(filename)
    repaint(canvas, top, width, height)

    # Hack to bring the window to the foreground
    tk.attributes('-topmost', True)
    tk.update()
    tk.attributes('-topmost', False)

    # TODO: Update on resize
    # TODO: Handle clicks
    # TODO: Handle commands

    tk.mainloop()
