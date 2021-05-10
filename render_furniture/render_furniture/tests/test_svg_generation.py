"""WIP
- scratch.
"""

import drawSvg as draw
import pytest

from render_furniture.schemas import Body, PlaneChoices
from render_furniture.renderer import (
    _geometry2rectangle,
    _sorted_rectangles,
    _remove_overlapped,
)


@pytest.mark.parametrize("plane", list(PlaneChoices))
def test_body_schema(original_example_input, plane):

    body = Body.parse_obj(original_example_input)

    rectangles = list(
        map(lambda g: _geometry2rectangle(plane=plane, geometry=g), body.geometry)
    )
    rectangles = _sorted_rectangles(rectangles)
    rectangles = _remove_overlapped(rectangles)
    rectangles.reverse()  # draw from furhtest to the closest one

    left_min = min(rectangles, key=lambda rect: rect.x).x
    right_max = max(rectangles, key=lambda rect: rect.x + rect.width)
    right_max = right_max.x + right_max.width

    bottom_min = min(rectangles, key=lambda rect: rect.y).y
    top_max = max(rectangles, key=lambda rect: rect.y + rect.height)
    top_max = top_max.y + top_max.height

    max_depth = max(rectangles, key=lambda rect: rect.depth).depth
    min_depth = min(rectangles, key=lambda rect: rect.depth).depth

    def _normalize_shade(depth, min_shade=150, max_shade=200):
        if max_depth == min_depth:
            return max_shade
        return (
            int((depth - min_depth) / (max_depth - min_depth) * (max_shade - min_shade))
            + min_shade
        )

    print("L", left_min)
    print("R", right_max)
    print("B", bottom_min)
    print("T", top_max)
    width = right_max - left_min
    print("W", width)
    height = top_max - bottom_min
    print("H", height)

    padding = int(0.1 * max(width, height))
    stroke_width = max(1, (0.001 * min(width, height)))

    d = draw.Drawing(width + padding * 2, height + padding * 2)
    for rectangle in rectangles:
        rectangle.x -= left_min - padding
        rectangle.y -= bottom_min - padding
        print(rectangle)
        shade = _normalize_shade(rectangle.depth)
        r = draw.Rectangle(
            rectangle.x,
            rectangle.y,
            rectangle.width,
            rectangle.height,
            fill="#{0:02x}{0:02x}{0:02x}".format(shade),
            stroke="black",
            stroke_width=stroke_width,
        )
        d.append(r)

    d.setPixelScale(2)
    d.saveSvg(f"example_{plane.name}.svg")
