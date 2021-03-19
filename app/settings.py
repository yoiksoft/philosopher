"""Application settings

One unified place to hold configurations for the application.
"""

import typing
import sentry_sdk 
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

from app import utils


# Initialize the Sentry SDK.
sentry_sdk.init(dsn=utils.config("SENTRY_DSN", default=None))


# Load whether or not to run the application in debug mode from config.
DEBUG = utils.config("DEBUG", cast=bool, default=False)


# Load any middleware to run with the application.
MIDDLEWARE: typing.Sequence[Middleware] = [
  Middleware(
    SentryAsgiMiddleware),
  Middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"])
]


# Collection of handlers for HTTP exceptions.
EXCEPTION_HANDLERS: typing.Sequence[typing.Tuple[int, typing.Callable]] = [
  (404, None),
  (500, None),
]


# Lifespan function to configure parts of the app that are needed throughout
# it's lifespan.
LIFESPAN: typing.AsyncGenerator = utils.lifespan
