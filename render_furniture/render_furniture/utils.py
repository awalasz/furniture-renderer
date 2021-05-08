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
from typing import List

from render_furniture.render_furniture.schemas import Body, Geometry, PlaneChoices, Rectangle


class Render(ABC):
    @abstractmethod
    def render(self, *args, **kwargs):
        pass


def geometry2rectangle(geometry: Geometry, plane: PlaneChoices) -> Rectangle:
    """ TODO - depending on the plane, Left and Right to the common users of furniture app would not be the same as
               negative and positive values on axis. I will handle this at the end. For now i just use axis values.

                 ^ Y                                ^ Y
                 |   123                      321   |
                 |   456  789            987  654   |
                 |_____________> X  -X <____________|
                /                                  /
               /                                  /
              V Z                                V Z

    :param geometry: Geometry object to be casted to flat rectangle with height property
    :param plane: plane to which geometry will be casted
    :return: "flat" Rectangle object with height property
    """
    if not isinstance(plane, PlaneChoices):
        raise TypeError("plane must be PlaneChoices enum instance")

    geometry = dict(geometry)

    x_attr, y_attr = plane.value.lower()[-2:]
    height_attr = list({"x", "y", "z"} - {x_attr, y_attr})[0]

    left = geometry[x_attr + "1"]
    right = geometry[x_attr + "2"]

    if "-" in plane.value.lower():  # is negated plane
        height = -min(geometry[height_attr + "1"], geometry[height_attr + "2"])
        left, right = -left, -right
    else:
        height = max(geometry[height_attr + "1"], geometry[height_attr + "2"])

    return Rectangle(
        left=left,
        right=right,
        top=geometry[y_attr + "1"],
        bottom=geometry[y_attr + "2"],
        height=height,
    )


def sorted_geometries(geometry: List[Geometry], plane: PlaneChoices) -> List[Geometry]:
    """Methods returns geometries in order from the closest to the further one, according to the selected plane.

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


def remove_shadowed_geometries(geometry: List[Geometry], plane: PlaneChoices) -> List[Geometry]:
    # todo. To many if-else here. I should cast 3d geometry to rectangle & depth first,
    #       which are independent from planes.
    raise NotImplemented()

    # sorted_geometry = sorted_geometries(geometry, plane)
    # # TODO - i was thinking to use functools.reduce, but it's not the case
    # closest = sorted_geometry[0]
    # for next_geometry in sorted_geometry[1:]:
    #     if all(
    #         next_geometry
    #     ):
    #
    # return output


class RenderSVG(Render):
    def __init__(self, data: Body):
        self.plane = data.projection_plane
        self.geometry = data.geometry

    def render(self, *args, **kwargs):
        print(self.plane, self.geometry)
        print(sorted_geometries(geometry=self.geometry, plane=self.plane))
