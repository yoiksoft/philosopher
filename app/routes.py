"""URL mappings to endpoints
"""

from starlette.routing import Route, Mount

from app.services import ping


# Routes for the application.
ROUTES = [
  Route(
    "/ping",
    endpoint=ping.handler,
    methods=["GET"],
    name="ping"),
]
