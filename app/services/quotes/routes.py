from starlette.routing import Route

from app.services.quotes import endpoints

ROUTES = [
  Route(
    "/",
    endpoint=endpoints.get_all_quotes,
    methods=["GET"],
  ),
  Route(
    "/",
    endpoint=endpoints.create_quote,
    methods=["POST"],
  ),
  Route(
    "/{quote_id:int}",
    endpoint=endpoints.get_one_quote,
    methods=["GET"],
  ),
  Route(
    "/{quote_id:int}",
    endpoint=endpoints.disown_quote,
    methods=["DELETE"],
  ),
  Route(
    "/{quote_id:int}/meanings",
    endpoint=endpoints.get_all_meanings,
    methods=["GET"],
  ),
  Route(
    "/{quote_id:int}/meanings",
    endpoint=endpoints.create_meaning,
    methods=["POST"],
  ),
]
