import sentry_sdk
from tortoise import Tortoise

from app.utils import config
from app.utils.redis import Redis
from app.utils.db import TORTOISE_ORM


async def lifespan(app):
  """Things to keep alive througout the lifespan of the app

  In this case we want a connection to Redis to persist throughout the lifespan 
  of the app.
  """

  # Initialize the Sentry SDK.
  sentry_sdk.init(dsn=config("SENTRY_DSN", default=None))

  # Create the Redis connection.
  url = config("REDIS_URL")
  redis = Redis()
  await redis.initialize(url=url)

  # Create the database connection.
  if config("ENVIRONMENT") == "development":
    TORTOISE_ORM["apps"]["models"]["models"].append("aerich.models")
  await Tortoise.init(config=TORTOISE_ORM)

  # Yield as the app runs.
  yield

  # Close the Redis connection once the app is shutting down.
  redis.connection.close()
  await redis.connection.wait_closed()

  # Close the Tortoise connection.
  await Tortoise.close_connections()
