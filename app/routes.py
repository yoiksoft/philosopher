"""URL mappings to endpoints
"""

from starlette.routing import Mount

from app.services.ping import routes as ping
from app.services.quotes import routes as quotes
from app.services.friends import routes as friends
from app.services.today import routes as today

# Routes for the application.
ROUTES = [
  Mount("/ping", routes=ping.ROUTES),
  Mount("/quotes", routes=quotes.ROUTES),
  Mount("/authors", routes=friends.ROUTES),
  Mount("/@today", routes=today.ROUTES),
]
