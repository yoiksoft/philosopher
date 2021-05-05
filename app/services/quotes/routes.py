from starlette.routing import Route

from app.services.quotes import endpoints


ROUTES = [
  Route(
    "/",
    endpoint=endpoints.get_all,
    methods=["GET"]),
  Route(
    "/",
    endpoint=endpoints.create,
    methods=["POST"]),
  Route(
    "/{quote_id:int}",
    endpoint=endpoints.get_one,
    methods=["GET"])
]
