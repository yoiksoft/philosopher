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


@requires_auth
async def submit(request: Request) -> JSONResponse:
  """Submit a quote for the day
  """

  # Alias the Redis connection.
  redis = request.app.state.redis

  # Get the user ID from request state.
  user_id = request.state.user["id"]

  # Determine if a submission has already been made.
  sub = await redis.get(user_id)
  if sub:
    return JSONResponse({
      "message": "You have already submitted a quote for today.",
      "data": sub
    }, status_code=200)

  # Get the quote from request body.
  data = await request.json()
  sub = data["quote"]

  # Write the submission to database.
  await redis.set(user_id, sub)

  # Return a success response.
  return JSONResponse({
    "message": "Successfully submitted quote for the day.",
    "data": sub
  }, status_code=201)