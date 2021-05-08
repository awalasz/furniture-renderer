"""
Tests for shadowing geometries. This method should sort geometries by depth (depending on plane) and check if
some of geometries are fully shadowed by other. In such situation wy may pop them from resulting list allowing us to
not render them.

Legend:
xxx : closer geometry
--- : further geometry

"""
import pytest

from render_furniture.render_furniture.schemas import Rectangle
from render_furniture.render_furniture.utils import remove_shadowed_geometries, is_shadowed


def test_partially_shadowed():
    """
    10 xxxxxxxxx
       x       x
    5  x       x----+
       x       x    |
    0  xxxxxxxxx    |
           |        |
    -5     +--------+
       0   5   10   15
    """
    close = Rectangle(height=10, left=0, right=10, bottom=0, top=10)
    far = Rectangle(height=0, left=5, right=15, bottom=-5, top=5)
    assert is_shadowed(top_rect=close, bottom_rect=far) is False


def test_not_overlapped():
    """
    xxxxxx    +----+
    x    x    |    |
    x    x    |    |
    xxxxxx    +----+
    """
    close = Rectangle(height=10, left=0, right=10, bottom=0, top=10)
    far = Rectangle(height=0, left=15, right=25, bottom=0, top=10)
    assert is_shadowed(top_rect=close, bottom_rect=far) is False


def test_fully_shadowed():
    """
    xxxxxxxxx
    x       x
    x  +--+ x
    x  +--+ x
    xxxxxxxxx
    """
    close = Rectangle(height=10, left=0, right=15, bottom=0, top=15)
    far = Rectangle(height=0, left=5, right=10, bottom=5, top=10)
    assert is_shadowed(top_rect=close, bottom_rect=far) is True


def test_smaller_over_big():
    """
    +--------+
    | xxxxx  |
    | x   x  |
    | xxxxx  |
    +--------+

    """
    close = Rectangle(height=10, left=5, right=10, bottom=5, top=10)
    far = Rectangle(height=0, left=0, right=15, bottom=0, top=15)
    assert is_shadowed(top_rect=close, bottom_rect=far) is False


def test_side_overlapping():
    """
        +x-x+xxxxx
        |   |    x
        x   |    x
        |---+    x
        xxxxxxxxxx

        """
    close = Rectangle(height=10, left=0, right=10, bottom=0, top=10)
    far = Rectangle(height=0, left=0, right=5, bottom=5, top=10)
    assert is_shadowed(top_rect=close, bottom_rect=far) is True
