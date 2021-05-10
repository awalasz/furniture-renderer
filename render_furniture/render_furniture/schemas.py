from enum import Enum
from typing import List

from pydantic import BaseModel, Extra


class PlaneChoices(Enum):
    XY = "XY"
    YZ = "YZ"
    XZ = "XZ"

    XY_rev = "-XY"
    YZ_rev = "-YZ"
    XZ_rev = "-XZ"


class Geometry(BaseModel, extra=Extra.forbid):
    x1: int
    x2: int
    y1: int
    y2: int
    z1: int
    z2: int


class Body(BaseModel):
    geometry: List[Geometry]
    projection_plane: PlaneChoices

    class Config:
        extra = Extra.forbid
        use_enum_values = True
