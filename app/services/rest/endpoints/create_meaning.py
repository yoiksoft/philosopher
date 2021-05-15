"""Endpoint to create a new Meaning for a Quote.
"""

from datetime import datetime
from aioredis import Redis
from starlette.requests import Request
from starlette.responses import JSONResponse
from tortoise.exceptions import ValidationError

from app.utils.auth import requires_auth, uses_user, User
from app.utils.redis import uses_redis
from app.services.rest.models import Quote, Meaning


@requires_auth
@uses_user
@uses_redis
async def handler(request: Request, redis: Redis, user: User) -> JSONResponse:
  """Handler to create a new Meaning for a Quote.
  """

  quote_id = request.path_params["quote_id"]
  day = datetime.utcnow().date().isoformat()

  quote: Quote = await Quote.filter(id=quote_id).first()

  if not quote:
    return JSONResponse(
      {"message": "Quote does not exist."},
      status_code=404,
    )

  if quote.author_id == user.user_id:
    return JSONResponse(
      {"message": "You cannot write Meanings for your own Quote."},
      status_code=403)

  friends = await redis.sismember(f"friends:{user.user_id}", quote.author_id)
  ballot = await redis.sscan(f"today:{day}:request:{user.user_id}")
  on_ballot = quote_id in ballot

  if not friends and not on_ballot:
    return JSONResponse(
      {"message": "You are not permitted to create a Meaning for this Quote."},
      status_code=403,
    )

  existing: Meaning = await Meaning.filter(
    author_id=user.user_id, quote=quote).first()

  if existing:
    return JSONResponse(
      {"message": "You have already submitted a Meaning for this Quote."},
      status_code=403,
    )

  try:
    request_body = await request.json()
  except:
    return JSONResponse(
      {"message": "Missing request body."},
      status_code=400,
    )

  try:
    body = request_body["body"]
  except KeyError:
    return JSONResponse(
      {"message": "Missing body field in request body."},
      status_code=400,
    )

  try:
    meaning = await Meaning.create(
      body=body, author_id=user.user_id, quote=quote)
  except ValidationError as exception:
    return JSONResponse(
      {
        "message": "Invalid body failed validation.",
        "data": str(exception)
      },
      status_code=400,
    )

  return JSONResponse(
    {
      "message": "Success.",
      "data": meaning.to_dict()
    },
    status_code=201,
  )
