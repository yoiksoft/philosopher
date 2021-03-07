"""URL mappings to endpoints
"""

from starlette.routing import Route, Mount

from app import endpoints


# Routes for the application.
ROUTES = [
  Route(
    "/ping",
    endpoint=endpoints.ping,
    methods=["GET", "OPTIONS"],
    name="ping"),
  Route(
    "/qod",
    endpoint=endpoints.qod,
    methods=["GET", "OPTIONS"],
    name="qod"),
  Route(
    "/quotes",
    endpoint=endpoints.quotes,
    methods=["GET", "OPTIONS"],
    name="quotes"),
  Route(
    "/vote",
    endpoint=endpoints.vote,
    methods=["POST", "OPTIONS"],
    name="vote"),
  Route(
    "/submit",
    endpoint=endpoints.submit,
    methods=["POST", "OPTIONS"],
    name="submit"),
]
