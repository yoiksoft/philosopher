"""Functions that are triggered by a route
"""

from starlette.requests import Request
from starlette.responses import JSONResponse

from app.auth import requires_auth


@requires_auth
async def ping(request: Request) -> JSONResponse:
  """Ping endpoint
  """

  # Alias the Redis connection.
  redis = request.app.state.redis

  # Fetch a response from Redis.
  response = await redis.ping()

  # Return the response.
  return JSONResponse({
    "message": f'{request.state.user["username"]}, {response}'
  }, status_code=200)
