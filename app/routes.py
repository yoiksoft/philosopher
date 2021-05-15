"""URL mappings to endpoints
"""

from starlette.routing import Mount

from app.services.rest import routes as rest

# Routes for the application.
ROUTES = [
  Mount("/", routes=rest.ROUTES),
]
