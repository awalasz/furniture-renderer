"""
Planes interpretation based on:
https://math.libretexts.org/Bookshelves/Calculus/Book%3A_Calculus_(OpenStax)/12%3A_Vectors_in_Space/12.2%3A_Vectors_in_Three_Dimensions

  ^ Z
  |
  0------> Y
 /
/X


Test casting this example this to Rectangles:
Geometry A:
Pa1 = ( 2,  1,  4)    Pb1 = ( 2, 12,  4)
Pa2 = (-1,  3,  8)    Pb2 = (-3,  5,  6)


            Pa2   Pb2
      _______      ___________________
     /     /|     /                  /|
    /_____/ |    /                  / |
    |     | |   /__________________/ /
    | A   |/   |   B              | /
    |_____/    |__________________|/
   Pa1                           Pb1

  ^ Z
  |
  0------> Y
 /
/X

"""
import pytest

from render_furniture.render_furniture.schemas import Geometry, Rectangle, PlaneChoices
from render_furniture.render_furniture.utils import geometry2rectangle

A = Geometry(x1=2, y1=1, z1=4, x2=-1, y2=3, z2=8)
B = Geometry(x1=2, y1=12, z1=4, x2=-3, y2=5, z2=6)


@pytest.mark.parametrize(
    "plane, expected_a, expected_b",
    [
        (
            PlaneChoices.XY,
            Rectangle(left=-1, right=2, bottom=1, top=3, height=8),
            Rectangle(left=-3, right=2, bottom=5, top=12, height=6),
        ),
        (
            PlaneChoices.YZ,
            Rectangle(left=1, right=3, bottom=4, top=8, height=2),
            Rectangle(left=5, right=12, bottom=4, top=6, height=2),
        ),
        (
            PlaneChoices.XZ,
            Rectangle(left=2, right=-1, bottom=4, top=8, height=3),
            Rectangle(left=2, right=-3, bottom=4, top=6, height=12),
        ),  # TODO - this test if failing because of my Right and Left side interpretation. To validate later.
    ],
)
def test_casting_to_2d(plane, expected_a, expected_b):
    ra = geometry2rectangle(geometry=A, plane=plane)
    rb = geometry2rectangle(geometry=B, plane=plane)

    assert ra == expected_a
    assert rb == expected_b


"""
TODO:
Negated plane example:

      ^ Z                                ^ Z
      |   123                      321   |
      |   456  789            987  654   |
      |_____________> Y  -Y <____________|
     /                                  /
    /                                  /
   V X                                V X
"""
