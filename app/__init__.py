"""Main application entrypoint

This is where the application is instantiated.
"""

from starlette.applications import Starlette

from app import settings
from app import routes

# Instantiate the application
app: Starlette = Starlette(
  debug=settings.DEBUG,
  routes=routes.ROUTES,
  middleware=settings.MIDDLEWARE,
  exception_handlers=settings.EXCEPTION_HANDLERS,
  lifespan=settings.LIFESPAN)
