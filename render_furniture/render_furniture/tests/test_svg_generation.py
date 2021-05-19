"""WIP
- scratch.
"""
import django
import pytest
from django.test import Client

from render_furniture.renderer import render_svg
from render_furniture.schemas import Body, PlaneChoices


@pytest.mark.parametrize("plane", list(PlaneChoices))
def test_body_schema(original_example_input, plane):
    body = Body.parse_obj(original_example_input)
    output_svg = render_svg(geometries=body.geometry, plane=plane)
    with open(f"example_{plane.name}.svg", "w") as file:
        file.write(output_svg)


@pytest.fixture()
def client():
    django.setup()
    return Client(SERVER_NAME="localhost")


class TestProjectionsEndpoint:
    def test_produces_xml_svg_content(self, client, original_example_input):
        response = client.post("/projection", original_example_input, content_type="application/json")
        assert response.headers["Content-Type"] == "image/svg+xml"
        assert response.status_code == 200

    def test_produces_correct_output(
        self, client
    ):  # Parametrize this with examples of correct output (only Regression tests?)
        raise NotImplemented()

    def test_produces_output_with_correct_number_of_rectangles_if_no_projections_overlap(self, client):
        raise NotImplemented()

    def test_contains_only_rectangles_not_fully_obscured_by_other_rectangles(self, client):
        raise NotImplemented()

    def test_returns_400_if_incorrect_input_is_provided(self, client):
        response = client.post("/projection", {"invalid": "schema"}, content_type="application/json")
        assert response.status_code == 400
