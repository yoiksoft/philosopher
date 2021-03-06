"""URL mappings to endpoints
"""

from starlette.routing import Route, Mount

from app import endpoints


# Routes for the application.
ROUTES = [
  Route("/ping", endpoint=endpoints.ping, methods=["GET"], name="ping"),
  Route("/qod", endpoint=endpoints.qod, methods=["GET"], name="qod"),
  Route("/quotes", endpoint=endpoints.quotes, methods=["GET"], name="quotes"),
  Route("/vote", endpoint=endpoints.vote, methods=["POST"], name="vote"),
  Route("/submit", endpoint=endpoints.submit, methods=["POST"], name="submit"),
]
