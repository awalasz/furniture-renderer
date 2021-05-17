"""
The first used interpretation of planes based on:
https://math.libretexts.org/Bookshelves/Calculus/Book%3A_Calculus_(OpenStax)/12%3A_Vectors_in_Space/12.2%3A_Vectors_in_Three_Dimensions
wasn't match example input.json in which plane XY was the front of furniture. I decided to reorganize axes to this:

ROTATION

  ^ Y
  |
  0------> X
 /
/Z

Then, negation of "Z" ( -to fit left and right from users perspective)

 Y^ /Z
  |/
  0------> X


Test casting this example this to Rectangles:
Geometry A:
Pa1 = (1,  4,  2)    Pb1 = (12,  4,  2)
Pa2 = (3,  8, -1)    Pb2 = ( 5,  6, -3)


            Pa2   Pb2
      _______      ___________________
     /     /|     /                  /|
    /_____/ |    /                  / |
    |     | |   /__________________/ /
    | A   |/   |   B              | /
    |_____/    |__________________|/
   Pa1                           Pb1

  ^ Y
  |
  0------> X
 /
/Z

EXPECTED RESULTS:
XY plane:
8 +-----+
  |     |
6 |     |    +-------------------+
  |     |    |                   |
4 +-----+    +-------------------+
  1     3    5                  12

YZ plane:
8 +------+
  |      |
6 +--------------+
  |      :       |
4 +------+-------+
 -2      1       3

XZ plane:
           3 +-------------------+
             |                   |
             |                   |
             |                   |
1 +-----+    |                   |
  |     |    |                   |
  |     +    |                   |
-2+-----+    +-------------------+
  1     3    5                  12

"""
import pytest

from render_furniture.renderer import Rectangle, _geometry2rectangle
from render_furniture.schemas import Geometry, PlaneChoices

A = Geometry(x1=1, y1=4, z1=2, x2=3, y2=8, z2=-1)
B = Geometry(x1=12, y1=4, z1=2, x2=5, y2=6, z2=-3)


@pytest.mark.parametrize(
    "plane, expected_a, expected_b",
    [
        (
            PlaneChoices.X_Y,
            Rectangle(x=1, width=2, y=4, height=4, depth=2),
            Rectangle(x=5, width=7, y=4, height=2, depth=2),
        ),
        (
            PlaneChoices.Y_Z,
            Rectangle(x=-2, width=3, y=4, height=4, depth=3),
            Rectangle(x=-2, width=5, y=4, height=2, depth=12),
        ),
        (
            PlaneChoices.X_Z,
            Rectangle(x=1, width=2, y=-2, height=3, depth=8),
            Rectangle(x=5, width=7, y=-2, height=5, depth=6),
        ),
    ],
)
def test_casting_geometry_to_2d_gives_expected_rectangle(plane, expected_a, expected_b):
    ra = _geometry2rectangle(geometry=A, plane=plane)
    rb = _geometry2rectangle(geometry=B, plane=plane)

    assert ra == expected_a
    assert rb == expected_b
