from django.http import HttpResponse
from django.views import View
from pydantic.error_wrappers import ValidationError

from render_furniture.schemas import Body, PlaneChoices

from render_furniture.renderer import render_svg


class RenderSVGView(View):
    def post(self, request):
        try:
            parsed_body = Body.parse_raw(request.body)
        except ValidationError as e:
            return HttpResponse(e.json(), content_type="application/json", status=400)
        svg = render_svg(
            geometries=parsed_body.geometry, plane=PlaneChoices(parsed_body.projection_plane)
        )
        return HttpResponse(svg, content_type="image/svg+xml", status=200)
