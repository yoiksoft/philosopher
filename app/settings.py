"""Application settings

One unified place to hold configurations for the application.
"""

import typing
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

from app import utils
from app.utils.auth import AuthMiddleware
from app.utils.lifespan import get_lifespan

# Load whether or not to run the application in debug mode from config.
DEBUG = utils.config("DEBUG", cast=bool, default=False)

# Load any middleware to run with the application.
MIDDLEWARE: typing.Sequence[Middleware] = [
  Middleware(SentryAsgiMiddleware),
  Middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]),
  Middleware(AuthMiddleware),
]

# Collection of handlers for HTTP exceptions.
EXCEPTION_HANDLERS: typing.Sequence[typing.Tuple[int, typing.Callable]] = [
  (404, None),
  (500, None),
]

# Tortoise ORM configurations.
TORTOISE_ORM = {
  "connections": {
    "default": {
      "engine": "tortoise.backends.asyncpg",
      "credentials": {
        "host": utils.config("DB_HOST"),
        "port": utils.config("DB_PORT"),
        "user": utils.config("DB_USER"),
        "password": utils.config("DB_PASS"),
        "database": utils.config("DB_NAME"),
      },
    },
  },
  "apps": {
    "models": {
      "models": ["app.models", "aerich.models"],
      "default_connection": "default",
    },
  },
  "use_tz": False,
  "timezone": "UTC",
}

# Redis connection URL.
REDIS_URL = utils.config("REDIS_URL")

# Sentry DSN.
SENTRY_DSN = utils.config("SENTRY_DSN", default=None)

# Lifespan function to configure parts of the app that are needed throughout
# it's lifespan.
LIFESPAN: typing.AsyncGenerator = get_lifespan(
  sentry_dsn=SENTRY_DSN,
  redis_url=REDIS_URL,
  tortoise_config=TORTOISE_ORM,
)
