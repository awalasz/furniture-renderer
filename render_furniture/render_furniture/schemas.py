from pydantic import BaseModel, Extra
from typing import List
from enum import Enum


class PlaneChoices(Enum):
    XY = 'XY'
    YZ = 'YZ'
    XZ = 'XZ'


class Geometry(BaseModel, extra=Extra.forbid):
    x1: int
    x2: int
    y1: int
    y2: int
    z1: int
    z2: int


class Body(BaseModel, extra=Extra.forbid):
    geometry: List[Geometry]
    projection_plane: PlaneChoices
