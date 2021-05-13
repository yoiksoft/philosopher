"""Redis utilities.
"""

# pylint: disable=attribute-defined-outside-init

import aioredis

from app.utils import Singleton


class CreateRedisError(Exception):
  """Error to express a problem while creating a Redis connection.
  """


class Redis(Singleton):
  """Redis singleton.

  This way, Redis can be imported from anywhere, instantiated, and the same
  instance will always be returned. So, as long as the app has started
  properly, the connection will be initialized and Redis will be available for
  use.
  """

  def init(self, *args, **kwargs):
    """Start with empty connection
    """
    self.connection = None

  async def initialize(self, url):
    """Initialize the connection with this instance method.
    """

    if not self.connection:
      try:
        self.connection: aioredis.Redis = await aioredis.create_redis_pool(
          url, encoding="utf-8")
      except Exception as exception:
        raise CreateRedisError from exception


def uses_redis(func):
  """Redis connection wrapper.

  Wrapper for endpoinds that passes Redis connection down as a keyword
  argument.
  """

  async def inner(request, *args, **kwargs):
    redis = Redis()
    return await func(request, *args, redis=redis.connection, **kwargs)

  return inner
