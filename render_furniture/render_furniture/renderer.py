# TODO:
#  1. validation? Check if some Geometries has conflicts in space? Ignore for now.
#  3. rendering farest to cloesest.
#       - Normalized size of SVG? Then pringing scale would be helpfull
#       - color schema. Depending on depth - darker objects? (optional) - Not included in example output

from collections import namedtuple
from functools import lru_cache
from typing import List, Tuple, Literal
import drawSvg as draw

from pydantic import BaseModel

from render_furniture.schemas import (
    Geometry,
    PlaneChoices,
)

PlaneDescription = namedtuple("PlaneDescription", "x_axis, y_axis, depth_axis")


class Rectangle(BaseModel):
    x: int
    y: int
    width: int
    height: int

    depth: int


class AxisDescription(BaseModel):
    name: Literal["x", "y", "z"]
    negated: bool = False


@lru_cache
def _axes_by_plane(
    plane: PlaneChoices,
) -> PlaneDescription:
    """
    Based on the delivered input example, the
    axes were adjuted to generate furniture in the correct orientation from the perspective of the user. This means that
    furniture is visualized as it's standing on its base, not on its side.

    :param plane: PlaneChoices Enum object which should be translated.
    :return: PlaneDescription tuple which transits 3D axes to given 2D Plane.
    """
    return {
        PlaneChoices.XY: PlaneDescription(
            x_axis=AxisDescription(name="x"),
            y_axis=AxisDescription(name="y"),
            depth_axis=AxisDescription(name="z"),
        ),
        PlaneChoices.YZ: PlaneDescription(
            x_axis=AxisDescription(name="z", negated=True),
            y_axis=AxisDescription(name="y"),
            depth_axis=AxisDescription(name="x"),
        ),
        PlaneChoices.XZ: PlaneDescription(
            x_axis=AxisDescription(name="x"),
            y_axis=AxisDescription(name="z", negated=True),
            depth_axis=AxisDescription(name="y"),
        ),
        PlaneChoices.XY_rev: PlaneDescription(
            x_axis=AxisDescription(name="x", negated=True),
            y_axis=AxisDescription(name="y"),
            depth_axis=AxisDescription(name="z", negated=True),
        ),
        PlaneChoices.YZ_rev: PlaneDescription(
            x_axis=AxisDescription(name="z"),
            y_axis=AxisDescription(name="y"),
            depth_axis=AxisDescription(name="x", negated=True),
        ),
        PlaneChoices.XZ_rev: PlaneDescription(
            x_axis=AxisDescription(name="x"),
            y_axis=AxisDescription(name="z", negated=True),
            depth_axis=AxisDescription(name="y", negated=True),
        ),
    }.get(plane)


def _get_coordinate_and_length(
    geometry: Geometry, axis: AxisDescription
) -> Tuple[int, int]:
    a, b = getattr(geometry, f"{axis.name}1"), getattr(geometry, f"{axis.name}2")
    if axis.negated:
        a, b = -a, -b
    coordinate = min(a, b)
    length = abs(b - a)
    return coordinate, length


def _geometry2rectangle(geometry: Geometry, plane: PlaneChoices) -> Rectangle:
    """Method converts 3D geometry into 2D rectangle, casted to given plane.

                 ^ Y
                 |
                 |
                 |_____________> X
                /
               /
              V Z

    :param geometry: Geometry object to be casted to flat rectangle with depth property
    :param plane: plane to which geometry will be casted
    :return: "flat" Rectangle object with height property
    """
    if not isinstance(plane, PlaneChoices):
        raise TypeError("plane must be a PlaneChoices enum instance")

    plane_description = _axes_by_plane(plane)

    x, width = _get_coordinate_and_length(
        geometry=geometry, axis=plane_description.x_axis
    )
    y, height = _get_coordinate_and_length(
        geometry=geometry, axis=plane_description.y_axis
    )

    depth_1, depth_2 = getattr(
        geometry, plane_description.depth_axis.name + "1"
    ), getattr(geometry, plane_description.depth_axis.name + "2")
    if plane_description.depth_axis.negated:
        depth_1, depth_2 = -depth_1, -depth_2
    depth = max(depth_1, depth_2)

    return Rectangle(
        x=x,
        y=y,
        width=width,
        height=height,
        depth=depth,
    )


def _sorted_rectangles(rectangles: List[Rectangle]) -> List[Rectangle]:
    """Method returns sorted list of rectangles in order from closest to the further one, based on it's height"""
    return sorted(rectangles, key=lambda r: r.depth, reverse=True)


def _is_shadowed(top_rect: Rectangle, bottom_rect: Rectangle):
    """returns True if top_rect fully shadows bottom_rect"""
    # sanity check:
    if not top_rect.depth > bottom_rect.depth:
        return False

    return all(
        (
            top_rect.x <= bottom_rect.x <= (top_rect.x + top_rect.width),
            top_rect.x
            <= (bottom_rect.x + bottom_rect.width)
            <= (top_rect.x + top_rect.width),
            top_rect.y <= bottom_rect.y <= (top_rect.y + top_rect.height),
            top_rect.y
            <= (bottom_rect.y + bottom_rect.height)
            <= (top_rect.y + top_rect.height),
        )
    )


def _remove_overlapped(rectangles: List[Rectangle]) -> List[Rectangle]:
    """The method removes objects fully overlapped by others to potentially speed up rendering.

    Warning: This method only removes rectangles fully shadowed by other rectangle. This method do not remove rectangle
    fully shadowed by multiple other rectangles, but not fully by one of them

    DISCLAIMER:
    Since this removal is not crucial for resulting SVG output (This removal was introduced only to be used for
    speed up potentially slowly precessing of multiple figures during render) - I decided to skip that part.
    """
    sorted_rects = _sorted_rectangles(rectangles)
    not_shadowed = [sorted_rects[0]]
    for current_rect in sorted_rects[1:]:
        if all(
            not _is_shadowed(top_rect=r, bottom_rect=current_rect) for r in not_shadowed
        ):
            not_shadowed.append(current_rect)

    return not_shadowed


def render_svg(geometries: List[Geometry], plane: PlaneChoices) -> str:
    # TODO: cleanup.
    rectangles = list(
        map(lambda g: _geometry2rectangle(plane=plane, geometry=g), geometries)
    )
    rectangles = _sorted_rectangles(rectangles)
    rectangles = _remove_overlapped(rectangles)
    rectangles.reverse()  # draw from far to the closest one

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

    width = right_max - left_min
    height = top_max - bottom_min

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
    return d.asSvg()
