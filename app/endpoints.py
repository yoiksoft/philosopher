"""Functions that are triggered by a route
"""

import uuid
from datetime import datetime

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


async def qod(request: Request) -> JSONResponse:
  """Get the quote of the day.
  """

  # Alias the Redis connection.
  redis = request.app.state.redis

  # Get the date value.
  date = request.query_params.get('date')

  # Default to today.
  if not date:
    return JSONResponse({
      "message": "You must specify the date in query."
    }, status_code=400)

  # Get the quote of the day.
  res = await redis.zrevrangebyscore(f'{date}:scores', offset=0, count=1)
  
  if not res or date == datetime.utcnow().strftime("%Y-%m-%d"):
    return JSONResponse({
      "message": "There is no quote of the day from this date."
    }, status_code=200)

  user = res.pop()

  quote = await redis.get(f'{date}:user:{user}')

  # Return the quote of the day.
  return JSONResponse({
    "message": "Successfully got quote of the day!",
    "data": {
      "user": user,
      "qod": quote
    }
  })

@requires_auth
async def quotes(request: Request) -> JSONResponse:
  """Get two quotes to vote on.
  """

  # Alias the Redis connection.
  redis = request.app.state.redis

  # Get the user ID from request state.
  user_id = request.state.user["id"]

  # Get necessary date values.
  day = datetime.utcnow().strftime("%Y-%m-%d")

  if await redis.exists(f'{day}:request:{user_id}'):
    result = await redis.lrange(f'{day}:request:{user_id}', 0, -1)
  else:
    # Get two random members.
    result = await redis.srandmember(f'{day}:quotes', count=2)

    # Return a warning if there aren't enough quotes.
    if len(result) < 2:
      return JSONResponse({
        "message": "Not enough quotes yet. Come back later!"
      }, status_code=200)

    # Store those members in cache.
    await redis.rpush(f'{day}:request:{user_id}', *result)

  # Get their quotes.
  quotes = [await redis.get(f'{day}:user:{x}') for x in result]

  # Return the quotes
  return JSONResponse({
    "message": "Success",
    "data": quotes
  }, status_code=200)


@requires_auth
async def vote(request: Request) -> JSONResponse:
  """Vote on quotes
  """

  # Alias the Redis connection.
  redis = request.app.state.redis

  # Get the user ID from request state.
  user_id = request.state.user["id"]

  # Get necessary date values.
  day = datetime.utcnow().strftime("%Y-%m-%d")

  # Get the vote.
  try:
    body = await request.json()
  except:
    return JSONResponse({
      "message": "Missing request body."
    }, status_code=400)

  vote = body.get("vote")

  if not vote:
    return JSONResponse({
      "message": "Missing vote."
    }, status_code=400)

  # Return an error if invalid vote number.
  if vote > 2 or vote < 0:
    return JSONResponse({
      "message": "Invalid vote number."
    }, status_code=400)

  # If they voted with a skip.
  if vote == 2:
    await redis.delete(f'{day}:request:{user_id}')
    return JSONResponse({
      "message": "Successfuly skipped!"
    }, status_code=200)
  
  # Get the users.
  options = await redis.lrange(f'{day}:request:{user_id}', 0, -1)

  if not options:
    return JSONResponse({
      "message": "Missing quotes to vote from. Try requesting quotes first."
    }, status_code=400)

  # Specifically select the one the user voted for.
  try:
    winner = options[vote]
  except IndexError:
    return JSONResponse({
      "message": "Something went wrong."
    }, status_code=500)

  # Increment the winner score.
  await redis.zincrby(f'{day}:scores', 1, winner)

  # Reset the quote request.
  await redis.delete(f'{day}:request:{user_id}')

  return JSONResponse({
    "message": "Successfully voted!"
  }, status_code=200)


@requires_auth
async def submit(request: Request) -> JSONResponse:
  """Submit a quote for the day
  """

  # Alias the Redis connection.
  redis = request.app.state.redis

  # Get the user ID from request state.
  user_id = request.state.user["id"]

  # Get necessary date values.
  day = datetime.utcnow().strftime("%Y-%m-%d")

  # Determine if a submission has already been made.
  sub = await redis.get(f'{day}:user:{user_id}')
  if sub:
    return JSONResponse({
      "message": "You have already submitted a quote for today.",
      "data": sub
    }, status_code=200)

  # Get the quote from request body.
  data = await request.json()
  sub = data["quote"]

  # Write the submission to database.
  await redis.set(f'{day}:user:{user_id}', sub)
  await redis.sadd(f'{day}:quotes', user_id)

  # Return a success response.
  return JSONResponse({
    "message": "Successfully submitted quote for the day.",
    "data": sub
  }, status_code=201)