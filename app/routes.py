"""URL mappings to endpoints
"""

from starlette.routing import Route

from app import endpoints

# Routes for the application.
ROUTES = [
  # Get an author profile.
  Route(
    "/authors/{username}",
    endpoint=endpoints.get_author,
    methods=["GET"],
  ),
  # Get your relationship with an author.
  Route(
    "/authors/{username}/@me",
    endpoint=endpoints.get_relationship,
    methods=["GET"],
  ),
  # Get quotes from an author.
  Route(
    "/authors/{username}/quotes",
    endpoint=endpoints.get_quotes,
    methods=["GET"],
  ),
]
