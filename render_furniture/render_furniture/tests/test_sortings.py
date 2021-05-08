import pytest
from render_furniture.render_furniture.utils import sorted_geometries
from render_furniture.render_furniture.schemas import Geometry, PlaneChoices


x_close = Geometry(x1=5, x2=6, y1=-1, y2=1, z1=-1, z2=1)
x_far = Geometry(x1=-5, x2=-6, y1=-1, y2=1, z1=-1, z2=1)

y_close = Geometry(x1=-1, x2=1, y1=5, y2=6, z1=-1, z2=1)
y_far = Geometry(x1=-1, x2=1, y1=-5, y2=-6, z1=-1, z2=1)

z_close = Geometry(x1=-1, x2=1, y1=-1, y2=1, z1=5, z2=6)
z_far = Geometry(x1=-1, x2=1, y1=-1, y2=1, z1=-5, z2=-6)

geometries = [x_close, x_far, y_close, y_far, z_close, z_far]


@pytest.mark.parametrize(
    "plane, expected_closest, expected_farest",
    [
        (PlaneChoices.XY, z_close, z_far),
        (PlaneChoices.XZ, y_close, y_far),
        (PlaneChoices.YZ, x_close, x_far),
    ],
)
def test_sorting(plane, expected_closest, expected_farest):
    s = sorted_geometries(geometry=geometries, plane=plane)
    assert s[0] == expected_closest
    assert s[-1] == expected_farest


def test_sorting_surface():
    """
    --- ax1 - bx1 - ax2 - bx2 ---> X
    """
    ga = Geometry(x1=1, x2=3, y1=-1, y2=1, z1=-1, z2=1)
    gb = Geometry(x1=2, x2=4, y1=-1, y2=1, z1=-1, z2=1)
    s = sorted_geometries(geometry=[ga, gb], plane=PlaneChoices.YZ)
    assert s == [gb, ga]
    rev_s = sorted_geometries(geometry=[ga, gb], plane=PlaneChoices.YZ_rev)
    assert rev_s == [ga, gb]
