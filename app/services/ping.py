from starlette.responses import JSONResponse

from app.utils.auth import requires_auth, uses_user
from app.utils.redis import uses_redis

@uses_redis
@uses_user
async def handler(request, redis, user):
  """Ping endpoint
  """

  # Fetch a response from Redis.
  response = await redis.ping()

  # Return the response.
  return JSONResponse({
    "message": f'{response}',
    "user": user
  }, status_code=200)
