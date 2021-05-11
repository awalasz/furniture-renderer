# TODO:
#  1. validation? Check if some Geometries has conflicts in space? Ignore for now.
#  2. Optional - Normalized size of SVG? Then printing scale would be helpful
from collections import namedtuple
from typing import List, Tuple, Literal
import drawSvg as draw

from pydantic import BaseModel

from render_furniture.schemas import (
    Geometry,
    PlaneChoices,
)


class Rectangle(BaseModel):
    x: int
    y: int
    width: int
    height: int

    depth: int


class AxisDescription(BaseModel):
    name: Literal["x", "y", "z"]
    negated: bool = False


class PlaneDescription(BaseModel):
    x_axis: AxisDescription
    y_axis: AxisDescription
    depth_axis: AxisDescription


"""
Based on the delivered input example, the
axes were adjusted to generate furniture in the correct orientation from the perspective of the user. This means that
furniture is visualized as it's standing on its base, not on its side.

:param plane: PlaneChoices Enum object which should be translated.
:return: PlaneDescription tuple which transits 3D axes to given 2D Plane.
"""
_AXES_BY_PLANE = {
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
}


def _get_coordinate_and_length(geometry: Geometry, axis: AxisDescription) -> Tuple[int, int]:
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

    plane_description = _AXES_BY_PLANE[plane]

    x, width = _get_coordinate_and_length(geometry=geometry, axis=plane_description.x_axis)
    y, height = _get_coordinate_and_length(geometry=geometry, axis=plane_description.y_axis)

    depth_1, depth_2 = getattr(geometry, plane_description.depth_axis.name + "1"), getattr(
        geometry, plane_description.depth_axis.name + "2"
    )
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
    """returns True if the "top_rect" fully overlaps a bottom_rect"""
    # sanity check:
    if not top_rect.depth > bottom_rect.depth:
        return False

    return (
        top_rect.x <= bottom_rect.x <= (top_rect.x + top_rect.width)
        and top_rect.x <= (bottom_rect.x + bottom_rect.width) <= (top_rect.x + top_rect.width)
        and top_rect.y <= bottom_rect.y <= (top_rect.y + top_rect.height)
        and top_rect.y <= (bottom_rect.y + bottom_rect.height) <= (top_rect.y + top_rect.height)
    )


def _remove_overlapped(rectangles: List[Rectangle]) -> List[Rectangle]:
    """The method removes objects fully overlapped by others to potentially speed up rendering and decrease output SVG
    file size.

    Warning: This method only removes rectangles fully obscured by another single rectangle. This method does not remove
    rectangle fully shadowed by multiple other rectangles, but not fully by one of them

    DISCLAIMER:
    Since this removal is not crucial for resulting SVG output (This removal was introduced only to be used for speed up
    potentially slowly precessing of multiple figures during render) - I decided to skip the case described in the above
    warning but I am aware of it.
    """
    sorted_rects = _sorted_rectangles(rectangles)
    not_overlapped = [sorted_rects[0]]
    for current_rect in sorted_rects[1:]:
        if all(not _is_shadowed(top_rect=r, bottom_rect=current_rect) for r in not_overlapped):
            not_overlapped.append(current_rect)

    return not_overlapped


AxisRanges = namedtuple("AxisRanges", "x_min, x_max, y_min, y_max, depth_min, depth_max")


def _get_axis_range(rectangles: List[Rectangle]) -> AxisRanges:
    return AxisRanges(
        x_min=min(rect.x for rect in rectangles),
        x_max=max(rect.x + rect.width for rect in rectangles),
        y_min=min(rect.y for rect in rectangles),
        y_max=max(rect.y + rect.height for rect in rectangles),
        depth_min=min(rect.depth for rect in rectangles),
        depth_max=max(rect.depth for rect in rectangles),
    )


def _adjust_rectangles_position(
    rectangles: List[Rectangle], ranges: AxisRanges, padding: int, inplace=True
) -> List[Rectangle]:
    if not inplace:
        rectangles = rectangles[:]
    for rectangle in rectangles:
        rectangle.x -= ranges.x_min - padding
        rectangle.y -= ranges.y_min - padding
    return rectangles if not inplace else None


def render_svg(geometries: List[Geometry], plane: PlaneChoices) -> str:
    rectangles = [_geometry2rectangle(plane=plane, geometry=g) for g in geometries]
    rectangles = _sorted_rectangles(rectangles)
    rectangles = _remove_overlapped(rectangles)
    rectangles.reverse()  # draw from far to the closest one

    ranges = _get_axis_range(rectangles)

    width = ranges.x_max - ranges.x_min
    height = ranges.y_max - ranges.y_min

    padding = int(0.1 * max(width, height))
    stroke_width = max(1, (0.001 * min(width, height)))

    _adjust_rectangles_position(rectangles=rectangles, ranges=ranges, padding=padding)

    def _normalize_shade(depth, min_shade=150, max_shade=200):
        if ranges.depth_min == ranges.depth_max:
            return max_shade
        return (
            int(
                (depth - ranges.depth_min)
                / (ranges.depth_max - ranges.depth_min)
                * (max_shade - min_shade)
            )
            + min_shade
        )

    d = draw.Drawing(width + padding * 2, height + padding * 2)
    for rectangle in rectangles:
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
