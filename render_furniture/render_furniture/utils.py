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

from render_furniture.render_furniture.schemas import Body, Geometry, PlaneChoices


class Render(ABC):

    @abstractmethod
    def render(self, *args, **kwargs):
        pass


class RenderSVG(Render):

    def __init__(self, data: Body):
        self.plane = data.projection_plane
        self.geometry = data.geometry

    def render(self, plane: PlaneChoices, geometry: List[Geometry],  *args, **kwargs):
        print(plane, geometry)
        print(self._sorted_geometries())

    def _sorted_geometries(self) -> List[Geometry]:
        # todo - check in example which of 1/2 indexes are "closer"
        sort_method = {
            'XY': lambda g: min(g.z1, g.z2),
            'YZ': lambda g: min(g.x1, g.x2),
            'XZ': lambda g: min(g.y1, g.y2),
            # '-XY': lambda g: max(g.z1, g.z2),
            # '-YZ': lambda g: max(g.x1, g.x2),
            # '-XZ': lambda g: max(g.y1, g.y2),
        }.get(self.plane)

        return sorted(self.geometry, key=sort_method)
