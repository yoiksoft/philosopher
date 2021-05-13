"""Endpoints for the Ping service.
"""

from aioredis import Redis
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.utils.auth import requires_auth, uses_user, User
from app.utils.redis import uses_redis


@uses_redis
@requires_auth
@uses_user
async def ping(_request: Request, redis: Redis, user: User) -> JSONResponse:
  """Ping endpoint
  """

  # Fetch a response from Redis.
  response = await redis.ping()

  # Return the response.
  return JSONResponse(
    {
      "message": f'{response}',
      "user": user.to_dict()
    },
    status_code=200,
  )
