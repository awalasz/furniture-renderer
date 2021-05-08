import pytest
from render_furniture.render_furniture.schemas import Body, Geometry, PlaneChoices


def test_body_schema(original_example_input):
    Body.parse_obj(original_example_input)


def test_invalid_body_schema_from_example(original_example_input):
    original_example_input["plane"] = original_example_input.pop("projection_plane")
    with pytest.raises(ValueError):
        Body.parse_obj(original_example_input)


def test_body(original_example_input):
    parsed = Body.parse_obj(original_example_input)
    assert parsed.projection_plane == PlaneChoices.XY
    assert len(parsed.geometry) == 13
    assert all(isinstance(g, Geometry) for g in parsed.geometry)


def test_invalid_plane(original_example_input):
    original_example_input["projection_plane"] = "Foo"
    with pytest.raises(ValueError):
        Body.parse_obj(original_example_input)
