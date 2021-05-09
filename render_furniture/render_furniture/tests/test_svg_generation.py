"""WIP
- scratch.
"""

import drawSvg as draw
import pytest

from render_furniture.render_furniture.schemas import Body, PlaneChoices
from render_furniture.render_furniture.utils import geometry2rectangle


def _convert(g, p):
    print(g, "->", geometry2rectangle(plane=p, geometry=g))


@pytest.mark.parametrize("plane", list(PlaneChoices))
def test_body_schema(original_example_input, plane):

    body = Body.parse_obj(original_example_input)
    for g in body.geometry:
        _convert(g, body.projection_plane)

    rectangles = list(map(lambda g: geometry2rectangle(plane=plane, geometry=g), body.geometry))
    left_min = min(rectangles, key=lambda rect: rect.left).left
    right_max = max(rectangles, key=lambda rect: rect.right).right
    bottom_min = min(rectangles, key=lambda rect: rect.bottom).bottom
    top_max = max(rectangles, key=lambda rect: rect.top).top

    max_height = max(rectangles, key=lambda rect: rect.height).height
    min_height = min(rectangles, key=lambda rect: rect.height).height


    print("L", left_min)
    print("R", right_max)
    print("B", bottom_min)
    print("T", top_max)
    width = right_max - left_min
    print("W", width)
    height = top_max - bottom_min
    print("H", height)


    padding = int(0.1 * max(width, height))
    d = draw.Drawing(width + padding*2, height + padding*2)
    for i, rectangle in enumerate(rectangles):
        rectangle.left -= left_min - padding
        rectangle.right -= left_min - padding
        rectangle.bottom -= bottom_min - padding
        rectangle.top -= bottom_min - padding
        print(rectangle)
        hh = rectangle.top - rectangle.bottom
        ww = rectangle.right - rectangle.left
        r = draw.Rectangle(rectangle.left, rectangle.bottom, ww, hh, fill="#" + str(i) * 6)
        d.append(r)

    d.setPixelScale(2)
    d.saveSvg(f'example_{plane.name}.svg')