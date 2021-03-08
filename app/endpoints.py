"""Functions that are triggered by a route
"""

import uuid
from datetime import datetime

from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app import utils
from app.auth import requires_auth


@requires_auth
async def ping(request: Request):
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


async def qod(request: Request):
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
  
  # Prevent people from seeing Quote of the Day for current day.
  if not res or date == datetime.utcnow().strftime("%Y-%m-%d"):
    return Response(status_code=204)

  # Pop the user ID.
  user_id = res.pop()

  # Get the quote data from Redis.
  quote = await redis.get(f'{date}:user:{user_id}')

  # Get the rich user data from Discord.
  user = await utils.user(user_id)

  # Return the quote of the day.
  return JSONResponse({
    "message": "Successfully got quote of the day!",
    "data": {
      "user": f'{user.get("username", "unknown")}#{user.get("discriminator", "0000")}',
      "quote": quote
    }
  }, status_code=200)

@requires_auth
async def quotes(request: Request):
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
      return Response(status_code=204)

    # Store those members in cache.
    await redis.rpush(f'{day}:request:{user_id}', *result)

  # Get their quotes.
  quotes = [await redis.get(f'{day}:user:{x}') for x in result]

  # Return the quotes
  return JSONResponse({
    "message": "Success!",
    "data": quotes
  }, status_code=200)


@requires_auth
async def vote(request: Request):
  """Vote on quotes
  """

  # Alias the Redis connection.
  redis = request.app.state.redis

  # Get the user ID from request state.
  user_id = request.state.user["id"]

  # Get necessary date values.
  day = datetime.utcnow().strftime("%Y-%m-%d")

  print(request)
  # Get the vote.
  try:
    body = await request.json()
  except:
    return JSONResponse({
      "message": "Missing request body."
    }, status_code=400)

  print(body)
  vote = body.get("vote")
  print(vote)

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
    return Response(status_code=204)
  
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
async def submit(request: Request):
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
    return Response(status_code=204)

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