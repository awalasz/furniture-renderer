"""WIP
- scratch.
"""

import pytest

from render_furniture.schemas import Body, PlaneChoices
from render_furniture.renderer import render_svg


@pytest.mark.parametrize("plane", list(PlaneChoices))
def test_body_schema(original_example_input, plane):
    body = Body.parse_obj(original_example_input)
    output_svg = render_svg(geometries=body.geometry, plane=plane)
    with open(f"example_{plane.name}.svg", "w") as file:
        file.write(output_svg)


@pytest.fixture()
def rest_client():
    return None  # todo - use DRF?


class TestProjectionsEndpoint:
    def test_accepts_only_applications_json_content_type(self):
        raise NotImplemented()

    def test_produces_xml_svg_content(self):
        raise NotImplemented()

    def test_produces_correct_output(self):  # Parametrize this with examples of correct output (only Regression tests?)
        raise NotImplemented()

    def test_produces_output_with_correct_number_of_rectangles_if_no_projections_overlap(self):
        raise NotImplemented()

    def test_contains_only_rectangles_not_fully_obscured_by_other_rectangles(self):
        raise NotImplemented()

    def test_returns_400_if_incorrect_input_is_provided(self):
        raise NotImplemented()


# @lru_cache()
# def get_svg_renderer():
#     renderer_path = GET_RENDERER_PATH_FROM_SETTINGS  # obtain settings in Django
#     module, cls = renderer_path.rsplit(".", 1)
#     return getattr(__import__(renderer_path), cls)()
