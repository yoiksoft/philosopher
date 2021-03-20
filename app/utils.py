"""Application utilities

Functions and classes to help the application.
"""

import aiohttp
import aioredis
from starlette.config import Config


# Starlette helper class to load configurations from an environment file.
config: Config = Config(".env")
token = config("DISCORD_TOKEN")


async def user(user_id):
  """Get rich user data by user ID.
  """

  session = aiohttp.ClientSession(headers={ "Authorization": f"Bot {token}" })
  response = await session.get(f"https://discord.com/api/users/{user_id}")
  user = await response.json()
  await session.close()

  return user


def calculate_winnings(winners_score, losers_score):
  """Function to calculate winnings for the winning quote of a vote.

  Takes the winners current score and the losers current score, used to 
  influence the resulting winnings that will be applied to the winning quote. 
  Returns an integer representing the points to add to the winning quotes score.
  """

  return 1


async def lifespan(app):
  """Things to keep alive througout the lifespan of the app

  In this case we want a connection to Redis to persist throughout the lifespan 
  of the app.
  """

  # Create the Redis connection.
  url = config("REDIS_URL")
  redis = await aioredis.create_redis_pool(url, encoding="utf-8")

  # Bind the Redis connection to the app state.
  app.state.redis = redis

  # Yield as the app runs.
  yield

  # Close the Redis connection once the app is shutting down.
  redis.close()
  await redis.wait_closed()
