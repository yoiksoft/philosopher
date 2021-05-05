"""URL mappings to endpoints
"""

from starlette.routing import Route, Mount

from app.services.ping import routes as ping
from app.services.quotes import routes as quotes


# Routes for the application.
ROUTES = [
  Mount("/ping", routes=ping.ROUTES),
  Mount("/quotes", routes=quotes.ROUTES)
]
