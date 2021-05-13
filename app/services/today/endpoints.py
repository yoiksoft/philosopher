"""Endpoints for the Today service.
"""

from datetime import date
from datetime import datetime

from aioredis import Redis
from starlette.routing import Request
from starlette.responses import JSONResponse, Response
from starlette.background import BackgroundTask

from app.utils.redis import uses_redis
from app.utils.auth import requires_auth, uses_user, User

from app.services.today import tools
from app.services.quotes.models import Quote


@requires_auth
@uses_redis
async def qotd(request: Request, redis: Redis):
  """Get the Quote of the Day for a specific date.
  """

  day = request.query_params.get("date")

  if not day:
    return JSONResponse({"message": "You must specify the date in query."},
                        status_code=400)

  res = await redis.zrevrangebyscore(f"today:{day}:scores", offset=0, count=1)

  if not res or date == date.today().isoformat():
    return JSONResponse({"message": "Invalid date selection."}, status_code=400)

  quote_id = res.pop()

  quote = await Quote.filter(id=quote_id).first()
  author = await quote.get_author()

  return JSONResponse(
    {
      "message": "Success.",
      "data": {
        "quote": await quote.to_dict(),
        "author": author.to_dict()
      }
    },
    status_code=200)


@requires_auth
@uses_user
@uses_redis
async def get_quotes(_request: Request, redis: Redis, user: User):
  """Get a couple Quotes to vote on.
  """

  day = datetime.utcnow().date().isoformat()

  if await redis.exists(f"today:{day}:request:{user.user_id}"):
    result = await redis.sscan(f"today:{day}:request:{user.user_id}")
  else:
    if await redis.exists(f"today:background:{user.user_id}"):
      return Response(status_code=204)

    result = await redis.srandmember(f"today:{day}:quotes", count=2)

    if len(result) < 2:
      return Response(status_code=204)

    quote_a = await Quote.filter(id=result[0]).first()
    quote_b = await Quote.filter(id=result[1]).first()
    authored = user.user_id == quote_a.author_id or user.user_id == quote_b.author_id

    has_seen_a = await redis.sismember(
      f"today:{day}:seen:{user.user_id}",
      result[0],
    )
    has_seen_b = await redis.sismember(
      f"today:{day}:seen:{user.user_id}",
      result[1],
    )
    if not has_seen_a and not has_seen_b and not authored:
      await redis.sadd(f"today:{day}:request:{user.user_id}", *result)
      await redis.sadd(f"today:{day}:seen:{user.user_id}", *result)
    else:
      # Initiate a background task to get fresh quotes.
      today = datetime.utcnow().date()
      task = BackgroundTask(tools.fetch_in_background, today, user.user_id)
      return Response(
        status_code=204,
        background=task,
      )

  quotes = [await Quote.filter(id=quote_id).first() for quote_id in result]

  return JSONResponse(
    {
      "message": "Success.",
      "data": [await quote.to_dict() for quote in quotes]
    },
    status_code=200,
  )


@requires_auth
@uses_user
@uses_redis
async def vote(request: Request, redis: Redis, user: User):
  """Vote on a Quote on your voting ballot.
  """

  day = datetime.utcnow().date().isoformat()

  # Get the vote.
  try:
    request_body = await request.json()
  except:
    return JSONResponse(
      {"message": "Missing request body."},
      status_code=400,
    )

  try:
    user_vote = request_body["vote"]
  except KeyError:
    return JSONResponse(
      {"message": "Missing vote field in request body."},
      status_code=400,
    )

  # Process a skip if required.
  if user_vote == 0:
    await redis.delete(f"today:{day}:request:{user.user_id}")
    return JSONResponse(
      {"message": "Success."},
      status_code=200,
    )

  if not await redis.exists(f"today:{day}:request:{user.user_id}"):
    return JSONResponse(
      {"message": "Missing Quotes to vote from."},
      status_code=400,
    )

  if not await redis.sismember(f"today:{day}:request:{user.user_id}",
                               user_vote):
    return JSONResponse(
      {"message": "Invalid vote."},
      status_code=400,
    )

  await redis.zincrby(f"today:{day}:scores", 1, user_vote)
  await redis.delete(f"today:{day}:request:{user.user_id}")

  return JSONResponse(
    {"message": "Success."},
    status_code=200,
  )


@requires_auth
@uses_user
@uses_redis
async def submit_quote(request: Request, redis: Redis, user: User):
  """Submit a Quote for Quote of the Day.
  """

  day = datetime.utcnow().date().isoformat()

  # Determine if a submission has already been made.
  sub = await redis.get(f"today:{day}:user:{user.user_id}")
  if sub:
    return JSONResponse(
      {"message": "You have already submitted a Quote for today."},
      status_code=400,
    )

  # Get Quote ID from request body.
  try:
    request_body = await request.json()
  except:
    return JSONResponse(
      {"message": "Missing request body."},
      status_code=400,
    )

  try:
    quote_id = request_body["quote_id"]
  except KeyError:
    return JSONResponse(
      {"message": "Missing quote_id field in request body."},
      status_code=400,
    )

  quote = await Quote.filter(id=quote_id).first()

  if not quote or quote.author_id != user.user_id:
    return JSONResponse(
      {"message": "You cannot submit a Quote that you didn't write."},
      status_code=400,
    )

  quote_published = quote.published.strftime("%Y-%m-%d")

  if quote_published != day:
    return JSONResponse(
      {"message": "You can only submit Quotes that were written today."},
      status_code=400,
    )

  await redis.set(f"today:{day}:user:{user.user_id}", quote.id)
  await redis.sadd(f"today:{day}:quotes", quote.id)

  return JSONResponse(
    {"message": "Success."},
    status_code=200,
  )
