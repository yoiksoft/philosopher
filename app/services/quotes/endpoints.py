from aioredis import Redis
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.utils.auth import requires_auth, uses_user, User
from app.utils.redis import uses_redis
from app.services.quotes.models import Quote


@uses_redis
@requires_auth
@uses_user
async def get_all(request: Request, redis: Redis, user: User):
  """Get all quotes.
  """

  try:
    user_id = request.query_params["user_id"]
  except KeyError:
    return JSONResponse({
      "message": "Missing required query parameter 'user_id'"
    }, status_code=400)

  friends = await redis.sismember(f"friends:{user.user_id}", user_id)

  if not friends and user.user_id != user_id:
    return JSONResponse({
      "message": "You are not friends with this user"
    }, status_code=403)

  quotes = await Quote.filter(author_id=user_id)

  return JSONResponse({
    "message": "Success",
    "data": [(await quote.to_dict()) for quote in quotes]
  }, status_code=200)


@requires_auth
async def get_one(request: Request):
  """Get a specific quote.
  """

  qid = request.path_params["quote_id"]
  quote = await Quote.filter(id=qid).first()

  if not quote:
    return JSONResponse({
      "message": "Not found"
    }, status_code=404)
  
  return JSONResponse({
    "message": "Success",
    "data": await quote.to_dict()
  }, status_code=200)


@requires_auth
@uses_user
async def create(request: Request, user: User):
  """Create a new quote.
  """

  try:
    request_body = await request.json()
  except:
    return JSONResponse({
      "message": "Missing request body."
    }, status_code=400)
  
  body = request_body["body"]

  quote = await Quote.create(body=body, author_id=user.user_id)

  return JSONResponse({
    "message": "Success",
    "data": await quote.to_dict()
  }, status_code=201)
