"""
temp file. I will probably reorganize this code later.
"""

# TODO:
#  1. validation? Check if some Geometries has sonfilct in space? Ignore for now.
#  2. Sorting - closest to nearest, dependint on plane
#  2.5(optional) - determine not visible objects - skip in rendering?
#  3. rendering farest to cloesest.
#       - Normalized size of SVG? Then pringing scale would be helpfull
#       - color schema. Depending on depth - darker objects? (optional) - Not included in example output

# TODO: For now plane is literal Literal['XY', 'YZ', 'XZ']. I am considering introducing opposite planes, like '-XY'

from abc import ABC, abstractmethod
from collections import namedtuple
from functools import lru_cache
from typing import List, Tuple

from render_furniture.render_furniture.schemas import (
    Body,
    Geometry,
    PlaneChoices,
    Rectangle,
    AxisDescription,
)


class Render(ABC):
    @abstractmethod
    def render(self, *args, **kwargs):
        pass


PlaneDescription = namedtuple("PlaneDescription", "x_axis, y_axis, depth_axis")


@lru_cache
def _axes_by_plane(
    plane: PlaneChoices,
) -> PlaneDescription:
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


def geometry2rectangle(geometry: Geometry, plane: PlaneChoices) -> Rectangle:
    """TODO - depending on the plane, Left and Right to the common users of furniture app would not be the same as
               negative and positive values on axis.
               This is related to the XZ plane - Right is on negative X axis, Left on positive.
               I will handle this at the end. For now i just use axis values.

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


def sorted_rectangles(rectangles: List[Rectangle]) -> List[Rectangle]:
    """Method returns sorted list of rectangles in order from closest to the further one, based on it's height"""
    return sorted(rectangles, key=lambda r: r.depth, reverse=True)


def sorted_geometries(geometry: List[Geometry], plane: PlaneChoices) -> List[Geometry]:
    """Method returns geometries in order from the closest to the further one, according to the selected plane.

    Note: that opposite plane (if implemented) cannot just reverse the order because of that There is no restriction
    to that x1 should be closer than x2 therefore this methods takes "max" of them (or "min" for the opposite planes),
    to determine a distance to the "camera point".

    TODO:
        ---- (A.X1 = -3) ------ (A.X2 = -1) --- |0| ------ (B.X2 = 2) --- (B.X1 = 1) ----------> X  [Camera point]
    TODO: On plane "XZ" the closest is B.X1 or A.X1? This is not exactly determined. I assumed, that camera is at -> end

    :param geometry: List of Geometry objects to be sorted
    :param plane: XY / YZ / XZ / -XY / -YZ / -XZ
    :return: new list of sorted geometries
    """
    sort_method = {
        "XY": lambda g: max(g.z1, g.z2),
        "YZ": lambda g: max(g.x1, g.x2),
        "XZ": lambda g: max(g.y1, g.y2),
        "-XY": lambda g: -min(g.z1, g.z2),
        "-YZ": lambda g: -min(g.x1, g.x2),
        "-XZ": lambda g: -min(g.y1, g.y2),
    }.get(plane.value)

    return sorted(geometry, key=sort_method, reverse=True)


def is_shadowed(top_rect: Rectangle, bottom_rect: Rectangle):
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


def remove_shadowed(rectangles: List[Rectangle]) -> List[Rectangle]:
    """Warning: This method only removes rectangles fully shadowed by other rectangle. This method do not remove rectangle
    fully shadowed by multiple other rectangles, but not fully by one of them

    DISCLAIMER:
    Since this removal is not crucial for resulting SVG output (This removal was introduced only to be used for
    speed up potentially slowly precessing of multiple figures during render) - I decided to skip that part.
    """
    sorted_rects = sorted_rectangles(rectangles)
    not_shadowed = [sorted_rects[0]]
    for current_rect in sorted_rects[1:]:
        if all(
            not is_shadowed(top_rect=r, bottom_rect=current_rect) for r in not_shadowed
        ):
            not_shadowed.append(current_rect)

    return not_shadowed


class RenderSVG(Render):
    def __init__(self, data: Body):
        self.plane = data.projection_plane
        self.geometry = data.geometry

    def render(self, *args, **kwargs):
        print(self.plane, self.geometry)
        print(sorted_geometries(geometry=self.geometry, plane=self.plane))
