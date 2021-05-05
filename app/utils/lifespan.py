import sentry_sdk
from tortoise import Tortoise

from app.utils import config
from app.utils.redis import Redis


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
  db_url = config("DATABASE_URL")
  await Tortoise.init(
    db_url=db_url,
    modules={"models": ["app.models"]}
  )
  await Tortoise.generate_schemas()

  # Yield as the app runs.
  yield

  # Close the Redis connection once the app is shutting down.
  redis.connection.close()
  await redis.connection.wait_closed()