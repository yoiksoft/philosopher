"""URL mappings to endpoints
"""

from starlette.routing import Route

from app.endpoints import authors
from app.endpoints import quotes
from app.endpoints import meanings

# Routes for the application.
ROUTES = [
  # Get an author profile.
  Route(
    "/authors/{username}",
    endpoint=authors.get_author,
    methods=["GET"],
  ),
  # Get quotes from an author.
  Route(
    "/authors/{username}/quotes",
    endpoint=authors.get_quotes_from_author,
    methods=["GET"],
  ),
  # Get meanings from an author.
  Route(
    "/authors/{username}/meanings",
    endpoint=authors.get_meanings_from_author,
    methods=["GET"],
  ),

  # Create quote.
  Route(
    "/quotes",
    endpoint=quotes.create_quote,
    methods=["POST"],
  ),
  # Get quote.
  Route(
    "/quotes/{quote_id}",
    endpoint=quotes.get_quote,
    methods=["GET"],
  ),
  # Disown quote.
  Route(
    "/quotes/{quote_id}",
    endpoint=quotes.disown_quote,
    methods=["DELETE"],
  ),
  # Create meaning.
  Route(
    "/quotes/{quote_id}/meanings",
    endpoint=meanings.create_meaning,
    methods=["POST"],
  ),

  # Get meaning.
  Route(
    "/meanings/{meaning_id}",
    endpoint=meanings.get_meaning,
    methods=["GET"],
  ),
  # Disown meaning.
  Route(
    "/meanings/{meaning_id}",
    endpoint=meanings.disown_meaning,
    methods=["DELETE"],
  ),
]
