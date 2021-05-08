"""
Tests for shadowing geometries. This method should sort geometries by depth (depending on plane) and check if
some of geometries are fully shadowed by other. In such situation wy may pop them from resulting list allowing us to
not render them.

Legend:
xxx : closer geometry
--- : further geometry

"""
import pytest

from render_furniture.render_furniture.schemas import Geometry, PlaneChoices
from render_furniture.render_furniture.utils import remove_shadowed_geometries

CLOSE_X1 = 6
CLOSE_X2 = 5
FAR_X1 = 2
FAR_X2 = 1


@pytest.fixture
def plane():
    return PlaneChoices.YZ


def test_partially_shadowed(plane):
    """
    xxxxxxxxx
    x       x
    x       x--+
    x       x  |
    xxxxxxxxx  |
          |    |
          +----+
    """
    close = Geometry(x1=CLOSE_X1, x2=CLOSE_X2, y1=0, y2=10, z1=0, z2=10)
    far = Geometry(x1=FAR_X1, x2=FAR_X2, y1=5, y2=15, z1=5, z2=15)
    out = remove_shadowed_geometries([far, close], plane)
    assert out == [close, far]


def test_not_overlapped():
    """
    xxxxxx    +----+
    x    x    |    |
    x    x    |    |
    xxxxxx    +----+
    """
    close = Geometry(x1=CLOSE_X1, x2=CLOSE_X2, y1=0, y2=10, z1=0, z2=5)
    far = Geometry(x1=FAR_X1, x2=FAR_X2, y1=0, y2=10, z1=10, z2=15)
    out = remove_shadowed_geometries([far, close], plane)
    assert out == [close, far]



def test_fully_shadowed():
    """
    xxxxxxxxx
    x       x
    x  +--+ x
    x  +--+ x
    xxxxxxxxx
    """
    close = Geometry(x1=CLOSE_X1, x2=CLOSE_X2, y1=0, y2=15, z1=0, z2=15)
    far = Geometry(x1=FAR_X1, x2=FAR_X2, y1=5, y2=10, z1=5, z2=10)
    out = remove_shadowed_geometries([far, close], plane)
    assert out == [close]


def test_smaller_over_big():
    """
    +--------+
    | xxxxx  |
    | x   x  |
    | xxxxx  |
    +--------+

    """
    close = Geometry(x1=CLOSE_X1, x2=CLOSE_X2, y1=5, y2=10, z1=5, z2=10)
    far = Geometry(x1=FAR_X1, x2=FAR_X2, y1=0, y2=15, z1=0, z2=15)
    out = remove_shadowed_geometries([far, close], plane)
    assert out == [close, far]
