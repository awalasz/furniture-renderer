"""
Tests for shadowing geometries. This method should sort geometries by depth (depending on plane) and check if
some of geometries are fully shadowed by other. In such situation wy may pop them from resulting list allowing us to
not render them.

Legend:
xxx : closer geometry
--- : further geometry

"""
from render_furniture.render_furniture.schemas import Rectangle, Body
from render_furniture.render_furniture.utils import remove_shadowed, is_shadowed


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
    close = Rectangle(depth=10, left=0, right=10, bottom=0, top=10)
    far = Rectangle(depth=0, left=5, right=15, bottom=-5, top=5)
    assert is_shadowed(top_rect=close, bottom_rect=far) is False


def test_not_overlapped():
    """
    xxxxxx    +----+
    x    x    |    |
    x    x    |    |
    xxxxxx    +----+
    """
    close = Rectangle(depth=10, left=0, right=10, bottom=0, top=10)
    far = Rectangle(depth=0, left=15, right=25, bottom=0, top=10)
    assert is_shadowed(top_rect=close, bottom_rect=far) is False


def test_fully_shadowed():
    """
    xxxxxxxxx
    x       x
    x  +--+ x
    x  +--+ x
    xxxxxxxxx
    """
    close = Rectangle(depth=10, left=0, right=15, bottom=0, top=15)
    far = Rectangle(depth=0, left=5, right=10, bottom=5, top=10)
    assert is_shadowed(top_rect=close, bottom_rect=far) is True


def test_smaller_over_big():
    """
    +--------+
    | xxxxx  |
    | x   x  |
    | xxxxx  |
    +--------+

    """
    close = Rectangle(depth=10, left=5, right=10, bottom=5, top=10)
    far = Rectangle(depth=0, left=0, right=15, bottom=0, top=15)
    assert is_shadowed(top_rect=close, bottom_rect=far) is False


def test_side_overlapping():
    """
    +x-x+xxxxx
    |   |    x
    x   |    x
    |---+    x
    xxxxxxxxxx

    """
    close = Rectangle(depth=10, left=0, right=10, bottom=0, top=10)
    far = Rectangle(depth=0, left=0, right=5, bottom=5, top=10)
    assert is_shadowed(top_rect=close, bottom_rect=far) is True


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
    a = Rectangle(depth=1, left=2, right=8, bottom=2, top=3)
    b = Rectangle(depth=2, left=4, right=10, bottom=1, top=4)
    c = Rectangle(depth=3, left=0, right=6, bottom=0, top=5)
    d = Rectangle(depth=0, left=0, right=3, bottom=3, top=5)
    original_list = [a, b, c, d]
    res = remove_shadowed(rectangles=original_list)
    assert res == [c, b, a]
    assert original_list == [a, b, c, d]  # test if res was a copy.
