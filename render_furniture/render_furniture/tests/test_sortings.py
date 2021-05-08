import pytest
from render_furniture.render_furniture.utils import sorted_geometries, sorted_rectangles, geometry2rectangle
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
    --- ax1 - cx2 - bx1 - cx1 - ax2 - bx2 ---> X
    """
    ga = Geometry(x1=0, x2=4, y1=-1, y2=1, z1=-1, z2=1)
    gb = Geometry(x1=2, x2=5, y1=-1, y2=1, z1=-1, z2=1)
    gc = Geometry(x1=3, x2=1, y1=-1, y2=1, z1=-1, z2=1)

    s = sorted_geometries(geometry=[ga, gb, gc], plane=PlaneChoices.YZ)
    assert s == [gb, ga, gc]

    rev_s = sorted_geometries(geometry=[ga, gb, gc], plane=PlaneChoices.YZ_rev)
    assert rev_s == [ga, gc, gb]


def test_sort_returns_new_list():
    a = Geometry(x1=1, x2=2, y1=1, y2=2, z1=1, z2=2)
    b = Geometry(x1=11, x2=12, y1=1, y2=2, z1=1, z2=2)
    c = Geometry(x1=21, x2=22, y1=1, y2=2, z1=1, z2=2)

    original_list = [b, a, c]
    new_list = sorted_geometries(geometry=original_list, plane=PlaneChoices.YZ)

    assert original_list != new_list
    assert new_list == [c, b, a]


def test_sort_rectangles():
    a = Geometry(x1=1, x2=2, y1=1, y2=2, z1=1, z2=2)
    b = Geometry(x1=11, x2=12, y1=1, y2=2, z1=1, z2=2)
    c = Geometry(x1=21, x2=22, y1=1, y2=2, z1=1, z2=2)

    rectangles = list(map(lambda g: geometry2rectangle(plane=PlaneChoices.YZ, geometry=g), [b, a, c]))

    sorted_r = sorted_rectangles(rectangles=rectangles)
    assert sorted_r[0].height == 22
    assert sorted_r[1].height == 12
    assert sorted_r[2].height == 2
