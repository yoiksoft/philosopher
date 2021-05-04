"""Application utilities

Functions and classes to help the application.
"""

import json
import aiohttp
import aioredis
import sentry_sdk
from starlette.config import Config


# Starlette helper class to load configurations from an environment file.
config: Config = Config(".env")
client_id = config("AUTH0_CLIENT_ID")
client_secret = config("AUTH0_CLIENT_SECRET")


async def get_management_token(redis):
  """Get management token to use the Auth0 Management API.
  """

  # Check for cached token in Redis.
  token = await redis.get("philosopher:token")
  # If no cache, fetch new.
  if not token:

    # Send the request for a new token.
    session = aiohttp.ClientSession(headers={
      "Content-Type": "application/json"
    })
    response = await session.post(
      f"https://kwot.us.auth0.com/oauth/token",
      data=json.dumps({
        "client_id": client_id,
        "client_secret": client_secret,
        "audience": "https://kwot.us.auth0.com/api/v2/",
        "grant_type": "client_credentials"
      })
    )
    token_data = await response.json()
    await session.close()

    # Store the token data.
    print(token_data)
    token = token_data["access_token"]
    await redis.set("philosopher:token", token)
    
  # Return token.
  return token


def uses_redis(func):
  async def inner(request, *args, **kwargs):
    redis = request.app.state.redis
    return await func(request, *args, redis=redis, **kwargs)
  return inner


def uses_user(func):
  async def inner(request, *args, **kwargs):
    redis = request.app.state.redis
    user_data = await get_user(redis, request.state.user["sub"])
    return await func(request, *args, user=user_data, **kwargs)
  return inner


async def get_user(redis, user_id, fields = ["user_id", "username", "nickname", "name"]):
  """Get rich user data by user ID.
  """

  token = await get_management_token(redis)
  fields_string = ",".join(fields)

  session = aiohttp.ClientSession(headers={"Authorization": f"Bearer {token}"})
  response = await session.get(f"https://kwot.us.auth0.com/api/v2/users/{user_id}?fields={fields_string}&include_fields=true")
  user = await response.json()
  await session.close()

  return user


async def lifespan(app):
  """Things to keep alive througout the lifespan of the app

  In this case we want a connection to Redis to persist throughout the lifespan 
  of the app.
  """

  # Initialize the Sentry SDK.
  sentry_sdk.init(dsn=config("SENTRY_DSN", default=None))

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
