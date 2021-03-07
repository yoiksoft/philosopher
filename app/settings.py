"""Application settings

One unified place to hold configurations for the application.
"""

import typing
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from app import utils


# Load whether or not to run the application in debug mode from config.
DEBUG = utils.config("DEBUG", cast=bool, default=False)


# Load any middleware to run with the application.
MIDDLEWARE: typing.Sequence[Middleware] = [
  Middleware(CORSMiddleware, allow_origins=['*'])
]


# Collection of handlers for HTTP exceptions.
EXCEPTION_HANDLERS: typing.Sequence[typing.Tuple[int, typing.Callable]] = [
  (404, None),
  (500, None),
]


# Lifespan function to configure parts of the app that are needed throughout
# it's lifespan.
LIFESPAN: typing.AsyncGenerator = utils.lifespan
