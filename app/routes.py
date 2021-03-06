"""URL mappings to endpoints
"""

from starlette.routing import Route, Mount

from app import endpoints


# Routes for the application.
ROUTES = [
  Route("/ping", endpoint=endpoints.ping, methods=["GET"], name="ping"),
]
