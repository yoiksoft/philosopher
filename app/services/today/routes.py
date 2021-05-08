from starlette.routing import Route

from app.services.today import endpoints


ROUTES = [
  Route(
    "/quotes",
    endpoint=endpoints.get_quotes,
    methods=["GET"]),
  Route(
    "/vote",
    endpoint=endpoints.vote,
    methods=["POST"]),
  Route(
    "/submit",
    endpoint=endpoints.submit_quote,
    methods=["POST"])
]
