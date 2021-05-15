"""Routes.
"""

from starlette.routing import Mount, Route

from app.services.today import routes as today
from app.services.ping import routes as ping

from app.services.rest.endpoints import create_quote
from app.services.rest.endpoints import get_one_quote
from app.services.rest.endpoints import disown_quote
from app.services.rest.endpoints import get_all_meanings
from app.services.rest.endpoints import create_meaning
from app.services.rest.endpoints import get_author
from app.services.rest.endpoints import get_all_quotes
from app.services.rest.endpoints import get_friends
from app.services.rest.endpoints import accept_request
from app.services.rest.endpoints import remove_friend
from app.services.rest.endpoints import get_requests
from app.services.rest.endpoints import create_request
from app.services.rest.endpoints import delete_request

ROUTES = [
  Mount("/ping", routes=ping.ROUTES),
  Mount("/@today", routes=today.ROUTES),
  Route(
    "/quotes",
    endpoint=create_quote.handler,
    methods=["POST"],
  ),
  Route(
    "/quotes/{quote_id:int}",
    endpoint=get_one_quote.handler,
    methods=["GET"],
  ),
  Route(
    "/quotes/{quote_id:int}",
    endpoint=disown_quote.handler,
    methods=["DELETE"],
  ),
  Route(
    "/quotes/{quote_id:int}/meanings",
    endpoint=get_all_meanings.handler,
    methods=["GET"],
  ),
  Route(
    "/quotes/{quote_id:int}/meanings",
    endpoint=create_meaning.handler,
    methods=["POST"],
  ),
  Route(
    "/authors/{author}",
    endpoint=get_author.handler,
    methods=["GET"],
  ),
  Route(
    "/authors/{author}/quotes",
    endpoint=get_all_quotes.handler,
    methods=["GET"],
  ),
  Route(
    "/authors/{author}/friends",
    endpoint=get_friends.handler,
    methods=["GET"],
  ),
  Route(
    "/authors/{author}/friends",
    endpoint=accept_request.handler,
    methods=["POST"],
  ),
  Route(
    "/authors/{author}/friends/{friend}",
    endpoint=remove_friend.handler,
    methods=["DELETE"],
  ),
  Route(
    "/authors/{author}/requests",
    endpoint=get_requests.handler,
    methods=["GET"],
  ),
  Route(
    "/authors/{author}/requests/{requester}",
    endpoint=create_request.handler,
    methods=["PUT"],
  ),
  Route(
    "/authors/{author}/requests/{requester}",
    endpoint=delete_request.handler,
    methods=["DELETE"],
  ),
]
