from enum import Enum
from typing import List

from pydantic import BaseModel, Extra


class PlaneChoices(Enum):
    X_Y = "XY"
    Y_Z = "YZ"
    X_Z = "XZ"

    NX_Y = "-XY"
    NY_Z = "-YZ"
    NX_Z = "-XZ"


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
