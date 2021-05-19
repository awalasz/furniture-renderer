"""
Tests for shadowing geometries. This method should sort geometries by depth (depending on plane) and check if
some of geometries are fully shadowed by other. In such situation wy may pop them from resulting list allowing us to
not render them.

Legend:
xxx : closer geometry
--- : further geometry

"""
from render_furniture.renderer import (
    Rectangle,
    _remove_overlapped,
    _is_shadowed,
)


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
    close = Rectangle(z=10, x=0, width=10, y=0, height=10)
    far = Rectangle(z=0, x=5, width=10, y=-5, height=10)
    assert _is_shadowed(top_rect=close, bottom_rect=far) is False


def test_not_overlapped():
    """
    xxxxxx    +----+
    x    x    |    |
    x    x    |    |
    xxxxxx    +----+
    """
    close = Rectangle(z=10, x=0, width=5, y=0, height=10)
    far = Rectangle(z=0, x=10, width=5, y=0, height=10)
    assert _is_shadowed(top_rect=close, bottom_rect=far) is False


def test_fully_shadowed():
    """
    xxxxxxxxx
    x       x
    x  +--+ x
    x  +--+ x
    xxxxxxxxx
    """
    close = Rectangle(z=10, x=0, width=15, y=0, height=15)
    far = Rectangle(z=0, x=5, width=5, y=5, height=10)
    assert _is_shadowed(top_rect=close, bottom_rect=far) is True


def test_smaller_over_big():
    """
    +--------+
    | xxxxx  |
    | x   x  |
    | xxxxx  |
    +--------+

    """
    close = Rectangle(z=10, x=5, width=10, y=5, height=10)
    far = Rectangle(z=0, x=0, width=15, y=0, height=15)
    assert _is_shadowed(top_rect=close, bottom_rect=far) is False


def test_side_overlapping():
    """
    +x-x+xxxxx
    |   |    x
    x   |    x
    |---+    x
    xxxxxxxxxx

    """
    close = Rectangle(z=10, x=0, width=10, y=0, height=10)
    far = Rectangle(z=0, x=0, width=5, y=5, height=5)
    assert _is_shadowed(top_rect=close, bottom_rect=far) is True


def test_removing_fully_shadowed_rectangles():
    """
    in this example "A" WOULDN'T BE REMOVED:
    even if A is shadowed by C and B together, both "B" and "C" are not shadowing "A" individualy and this situation
    is not handled.

    order by height: C, B, A, D

    DCDCCCCCCCCCC
    C  D    BBBBCBBBBB
    DD DA A BA ACA A B
    C   A   B   C  A B
    C   A A B  ACA A B
    C       BBBBCBBBBB
    CCCCCCCCCCCCC
    """
    a = Rectangle(z=1, x=2, width=6, y=2, height=1)
    b = Rectangle(z=2, x=4, width=6, y=1, height=3)
    c = Rectangle(z=3, x=0, width=6, y=0, height=5)
    d = Rectangle(z=0, x=0, width=3, y=3, height=2)
    original_list = [a, b, c, d]
    res = _remove_overlapped(rectangles=original_list)
    assert res == [c, b, a]
    assert original_list == [a, b, c, d]  # test if res was a copy.
