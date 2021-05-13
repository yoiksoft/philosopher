"""Data access utilities.
"""

import typing
from aioredis import Redis

from app.utils.redis import Redis as RedisPool


async def are_friends(user_a: str, user_b: str) -> bool:
  """Check if two users are friends.
  """

  redis: Redis = RedisPool().connection

  result = await redis.sismember(f"friends:{user_a}", user_b)

  return result


async def has_requested(requester: str, recipient: str) -> bool:
  """Check if a user sent a friend request to another user.
  """

  redis: Redis = RedisPool().connection

  result = await redis.sismember(f"requests:{recipient}", requester)

  return result


async def make_friends(user_a: str, user_b: str) -> None:
  """Make two users into friends.
  """

  redis: Redis = RedisPool().connection

  await redis.srem(f"requests:{user_a}", user_b)
  await redis.srem(f"requests:{user_b}", user_a)
  await redis.sadd(f"friends:{user_a}", user_b)
  await redis.sadd(f"friends:{user_b}", user_a)

  return


async def remove_friends(user_a: str, user_b: str) -> None:
  """Remove two users as friends.
  """

  redis: Redis = RedisPool().connection

  await redis.srem(f"friends:{user_a}", user_b)
  await redis.srem(f"friends:{user_b}", user_a)

  return


async def make_request(requester: str, recipient: str) -> None:
  """Make a request.
  """

  redis: Redis = RedisPool().connection

  await redis.sadd(f"requests:{recipient}", requester)

  return


async def remove_request(requester: str, recipient: str) -> None:
  """Remove a request.
  """

  redis: Redis = RedisPool().connection

  await redis.srem(f"requests:{recipient}", requester)

  return


async def get_friends(user: str) -> typing.List[str]:
  """Get friends for a user.
  """

  redis: Redis = RedisPool().connection

  friends = []
  cursor = "0"
  while cursor != 0:
    cursor, data = await redis.sscan(f"friends:{user}", cursor=cursor)
    friends.extend(data)

  return friends


async def get_requests(user: str) -> typing.List[str]:
  """Get requests to a user.
  """

  redis: Redis = RedisPool().connection

  requests = []
  cursor = "0"
  while cursor != 0:
    cursor, data = await redis.sscan(f"requests:{user}", cursor=cursor)
    requests.extend(data)

  return requests
