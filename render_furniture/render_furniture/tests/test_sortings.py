import pytest
from render_furniture.render_furniture.renderer import (
    _sorted_rectangles,
    _geometry2rectangle,
)
from render_furniture.render_furniture.schemas import Geometry, PlaneChoices


x_close = Geometry(x1=5, x2=6, y1=-1, y2=1, z1=-1, z2=1)
x_far = Geometry(x1=-5, x2=-6, y1=-1, y2=1, z1=-1, z2=1)

y_close = Geometry(x1=-1, x2=1, y1=5, y2=6, z1=-1, z2=1)
y_far = Geometry(x1=-1, x2=1, y1=-5, y2=-6, z1=-1, z2=1)

z_close = Geometry(x1=-1, x2=1, y1=-1, y2=1, z1=5, z2=6)
z_far = Geometry(x1=-1, x2=1, y1=-1, y2=1, z1=-5, z2=-6)


@pytest.fixture
def geometries():
    return [x_close, x_far, y_close, y_far, z_close, z_far]


def _rectangles(geometry, plane):
    return list(
        map(lambda g: _geometry2rectangle(plane=plane, geometry=g), geometry)
    )


@pytest.mark.parametrize(
    "plane, expected_closest, expected_farest",
    [
        (PlaneChoices.XY, z_close, z_far),
        (PlaneChoices.XZ, y_close, y_far),
        (PlaneChoices.YZ, x_close, x_far),
        (PlaneChoices.XY_rev, z_far, z_close),
        (PlaneChoices.XZ_rev, y_far, y_close),
        (PlaneChoices.YZ_rev, x_far, x_close),
    ],
)
def test_sorting(plane, expected_closest, expected_farest, geometries):
    s = _sorted_rectangles(_rectangles(geometries, plane=plane))

    assert s[0] == _geometry2rectangle(geometry=expected_closest, plane=plane)
    assert s[-1] == _geometry2rectangle(geometry=expected_farest, plane=plane)


def test_sort_rectangles():
    a = Geometry(x1=1, x2=2, y1=1, y2=2, z1=1, z2=2)
    b = Geometry(x1=11, x2=12, y1=1, y2=2, z1=1, z2=2)
    c = Geometry(x1=21, x2=22, y1=1, y2=2, z1=1, z2=2)

    rectangles = _rectangles([b, a, c], plane=PlaneChoices.YZ)
    sorted_rect = _sorted_rectangles(rectangles=rectangles)
    assert sorted_rect[0].depth == 22
    assert sorted_rect[1].depth == 12
    assert sorted_rect[2].depth == 2

    rev_plane_rectangles = _rectangles([b, a, c], plane=PlaneChoices.YZ_rev)
    rev_sorted_rect = _sorted_rectangles(rectangles=rev_plane_rectangles)
    assert rev_sorted_rect[0].depth == -1
    assert rev_sorted_rect[1].depth == -11
    assert rev_sorted_rect[2].depth == -21


