"""
Tests for shadowing geometries. This method should sort geometries by depth (depending on plane) and check if
some of geometries are fully shadowed by other. In such situation wy may pop them from resulting list allowing us to
not render them.

Legend:
xxx : closer geometry
--- : further geometry

Example:

    xxxxxxxxx
    x       x
    x       x--+
    x       x  |
    xxxxxxxxx  |
          |    |
          +----+
"""

CLOSE_X1 = 6
CLOSE_X2 = 5
FURTHER_X1 = 2
FURTHER_X2 = 1

def test_partially_shadowed():
    """
    xxxxxxxxx
    x       x
    x       x--+
    x       x  |
    xxxxxxxxx  |
          |    |
          +----+
    """
    pass


def test_not_overlapped():
    """

    xxxxxx    +----+
    x    x    |    |
    x    x    |    |
    xxxxxx    +----+

    """
    pass


def test_fully_shadowed():
    """
    xxxxxxxxx
    x       x
    x  +--+ x
    x  +--+ x
    xxxxxxxxx

    """
    pass


def test_smaller_over_big():
    """
    +--------+
    | xxxxx  |
    | x   x  |
    | xxxxx  |
    +--------+

    """
    pass