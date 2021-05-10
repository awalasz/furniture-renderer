from ninja import NinjaAPI

from render_furniture.schemas import Body

api = NinjaAPI()


@api.post("/projection")
def add(request, item: Body):
    return item
