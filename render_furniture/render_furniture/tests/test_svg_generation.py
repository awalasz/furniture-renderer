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
