from collections import namedtuple
from typing import List, Tuple, Literal

import drawSvg as draw
from pydantic import BaseModel

from render_furniture.schemas import (
    Geometry,
    PlaneChoices,
)


class Rectangle(BaseModel):
    """
    The model represents 2D figure projection to a plane. The `x` and `y` attributes point to the lower-left corner of
    the projected rectangle. "Z" attribute is used to determine whether a rectangle is closer or farther to the "camera
    point" and is used for example to check if a given rectangle is obstructed by another. Z Is also used for sorting
    purposes.
    """

    x: int
    y: int
    width: int
    height: int
    z: int

    @property
    def x_right(self):
        return self.x + self.width

    @property
    def y_top(self):
        return self.y + self.height


class AxisDescription(BaseModel):
    name: Literal["x", "y", "z"]
    negated: bool = False


class PlaneDescription(BaseModel):
    x_axis: AxisDescription
    y_axis: AxisDescription
    z_axis: AxisDescription


# Based on the delivered input example, the axes were adjusted to generate furniture in the correct orientation from the
# perspective of the user. This means that furniture is visualized as it's standing on its base, not on its side.
_AXES_BY_PLANE = {
    PlaneChoices.X_Y: PlaneDescription(
        x_axis=AxisDescription(name="x"),
        y_axis=AxisDescription(name="y"),
        z_axis=AxisDescription(name="z"),
    ),
    PlaneChoices.Y_Z: PlaneDescription(
        x_axis=AxisDescription(name="z", negated=True),
        y_axis=AxisDescription(name="y"),
        z_axis=AxisDescription(name="x"),
    ),
    PlaneChoices.X_Z: PlaneDescription(
        x_axis=AxisDescription(name="x"),
        y_axis=AxisDescription(name="z", negated=True),
        z_axis=AxisDescription(name="y"),
    ),
    PlaneChoices.NX_Y: PlaneDescription(
        x_axis=AxisDescription(name="x", negated=True),
        y_axis=AxisDescription(name="y"),
        z_axis=AxisDescription(name="z", negated=True),
    ),
    PlaneChoices.NY_Z: PlaneDescription(
        x_axis=AxisDescription(name="z"),
        y_axis=AxisDescription(name="y"),
        z_axis=AxisDescription(name="x", negated=True),
    ),
    PlaneChoices.NX_Z: PlaneDescription(
        x_axis=AxisDescription(name="x"),
        y_axis=AxisDescription(name="z", negated=True),
        z_axis=AxisDescription(name="y", negated=True),
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

    :param geometry: Geometry object to be casted to flat rectangle with "z" property
    :param plane: plane to which geometry will be casted
    :return: "flat" Rectangle object with height property
    """
    if not isinstance(plane, PlaneChoices):
        raise TypeError("plane must be a PlaneChoices enum instance")

    plane_description = _AXES_BY_PLANE[plane]

    x, width = _get_coordinate_and_length(geometry=geometry, axis=plane_description.x_axis)
    y, height = _get_coordinate_and_length(geometry=geometry, axis=plane_description.y_axis)

    z1 = getattr(geometry, plane_description.z_axis.name + "1")
    z2 = getattr(geometry, plane_description.z_axis.name + "2")
    if plane_description.z_axis.negated:
        z1, z2 = -z1, -z2

    return Rectangle(
        x=x,
        y=y,
        width=width,
        height=height,
        z=max(z1, z2),
    )


def _sorted_rectangles(rectangles: List[Rectangle]) -> List[Rectangle]:
    """Method returns sorted list of rectangles in order from closest to the further one, based on it's "z" attribute
    (axis that is perpendicular to the plane view"""
    return sorted(rectangles, key=lambda r: r.z, reverse=True)


def _is_shadowed(top_rect: Rectangle, bottom_rect: Rectangle):
    """returns True if the "top_rect" fully overlaps a bottom_rect"""
    # sanity check:
    if not top_rect.z > bottom_rect.z:
        return False

    left_side_obstructed = top_rect.x <= bottom_rect.x <= top_rect.x_right
    right_side_obstructed = top_rect.x <= bottom_rect.x_right <= top_rect.x_right
    bottom_side_obstructed = top_rect.y <= bottom_rect.y <= top_rect.y_top
    top_side_obstructed = top_rect.y <= bottom_rect.y_top <= top_rect.y_top

    return all([left_side_obstructed, right_side_obstructed, bottom_side_obstructed, top_side_obstructed])


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


AxisRanges = namedtuple("AxisRanges", "x_min, x_max, y_min, y_max, z_min, z_max")


def _get_axis_range(rectangles: List[Rectangle]) -> AxisRanges:
    """Calculates the most outer coordinates to determine the correct SVG view box"""
    x_min = rectangles[0].x
    x_max = rectangles[0].x_right
    y_min = rectangles[0].y
    y_max = rectangles[0].y_top
    z_min = z_max = rectangles[0].z
    for rectangle in rectangles[1:]:
        x_min = min(rectangle.x, x_min)
        x_max = max(rectangle.x_right, x_max)
        y_min = min(rectangle.y, y_min)
        y_max = max(rectangle.y_top, y_max)
        z_min = min(rectangle.z, z_min)
        z_max = max(rectangle.z, z_max)

    return AxisRanges(x_min=x_min, x_max=x_max, y_min=y_min, y_max=y_max, z_min=z_min, z_max=z_max)


def render_svg(geometries: List[Geometry], plane: PlaneChoices) -> str:
    rectangles = [_geometry2rectangle(plane=plane, geometry=g) for g in geometries]
    rectangles = _sorted_rectangles(rectangles)
    rectangles = _remove_overlapped(rectangles)

    ranges = _get_axis_range(rectangles)

    width = ranges.x_max - ranges.x_min
    height = ranges.y_max - ranges.y_min

    padding = int(0.1 * max(width, height))
    stroke_width = max(1, (0.001 * min(width, height)))

    def _normalize_shade(z, min_shade=150, max_shade=200):
        if ranges.z_min == ranges.z_max:
            return max_shade
        return int((z - ranges.z_min) / (ranges.z_max - ranges.z_min) * (max_shade - min_shade)) + min_shade

    d = draw.Drawing(
        width + padding * 2,
        height + padding * 2,
        origin=(ranges.x_min - padding, ranges.y_min - padding),
    )
    for rectangle in reversed(rectangles):
        shade = _normalize_shade(rectangle.z)
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
