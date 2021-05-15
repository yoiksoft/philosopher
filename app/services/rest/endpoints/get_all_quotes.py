"""Endpoint to get all Quotes.
"""

from aioredis import Redis
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.utils.auth import requires_auth, uses_user, User, get_user_by_nickname
from app.utils.redis import uses_redis
from app.services.rest.models import Quote


@requires_auth
@uses_user
@uses_redis
async def handler(request: Request, redis: Redis, user: User) -> JSONResponse:
  """Handler to get all Quotes.
  """

  author_nickname = request.path_params["author"]
  author: User = await get_user_by_nickname(author_nickname)

  if not author:
    return JSONResponse({"message": "Author not found."}, status_code=404)

  friends = await redis.sismember(f"friends:{user.user_id}", author.user_id)

  if not friends and user.user_id != author.user_id:
    return JSONResponse(
      {"message": "You are not friends with this user."},
      status_code=403,
    )

  quotes = await Quote.filter(author_id=author.user_id)

  return JSONResponse(
    {
      "message": "Success.",
      "data": [quote.to_dict() for quote in quotes]
    },
    status_code=200,
  )
