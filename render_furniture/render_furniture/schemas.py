from pydantic import BaseModel
from typing import List, Literal


class Geometry(BaseModel):
    x1: int
    x2: int
    y1: int
    y2: int
    z1: int
    z2: int


class Body(BaseModel):
    geometry: List[Geometry]
    projection_plane: Literal['XY', 'YZ', 'XZ']
