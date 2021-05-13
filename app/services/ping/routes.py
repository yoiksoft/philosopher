"""Routes for the Ping service.
"""

from starlette.routing import Route

from app.services.ping import endpoints

ROUTES = [
  Route(
    "/",
    endpoint=endpoints.ping,
    methods=["GET"],
  ),
]
