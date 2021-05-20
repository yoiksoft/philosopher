"""Lifespan utilities.
"""

# pylint: disable=abstract-class-instantiated

import typing
import sentry_sdk
from tortoise import Tortoise
from starlette.applications import Starlette

from app.utils.redis import Redis


def get_lifespan(
  sentry_dsn: str,
  redis_url: str,
  tortoise_config: dict,
) -> typing.AsyncGenerator:
  """Generator to return a lifespan function.

  Passes configuration from settings to the lifespan function.
  """

  async def lifespan(_app: Starlette):
    """Things to keep alive througout the lifespan of the app

    In this case we want a connection to Redis to persist throughout the lifespan
    of the app.
    """

    # Initialize the Sentry SDK.
    sentry_sdk.init(dsn=sentry_dsn)

    # Create the Redis connection.
    redis = Redis()
    await redis.initialize(url=redis_url)

    # Create the database connection.
    await Tortoise.init(config=tortoise_config)

    # Yield as the app runs.
    yield

    # Close the Redis connection once the app is shutting down.
    redis.connection.close()
    await redis.connection.wait_closed()

    # Close the Tortoise connection.
    await Tortoise.close_connections()

  return lifespan
