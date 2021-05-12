from datetime import datetime
from aioredis import Redis
from starlette.requests import Request
from starlette.responses import JSONResponse
from tortoise.exceptions import ValidationError

from app.utils.auth import requires_auth, uses_user, User
from app.utils.redis import uses_redis
from app.services.quotes.models import Quote, Meaning


@uses_redis
@requires_auth
@uses_user
async def get_all_quotes(request: Request, redis: Redis, user: User):
  """Get all Quotes.
  """

  try:
    user_id = request.query_params["user_id"]
  except KeyError:
    return JSONResponse(
      {"message": "Missing required query parameter."},
      status_code=400,
    )

  friends = await redis.sismember(f"friends:{user.user_id}", user_id)

  if not friends and user.user_id != user_id:
    return JSONResponse(
      {"message": "You are not friends with this user."},
      status_code=403,
    )

  quotes = await Quote.filter(author_id=user_id)

  return JSONResponse(
    {
      "message": "Success.",
      "data": [(await quote.to_dict()) for quote in quotes]
    },
    status_code=200,
  )


@requires_auth
async def get_one_quote(request: Request):
  """Get a specific Quote.
  """

  qid = request.path_params["quote_id"]
  quote = await Quote.filter(id=qid).first()

  if not quote:
    return JSONResponse(
      {"message": "Not found."},
      status_code=404,
    )

  return JSONResponse(
    {
      "message": "Success.",
      "data": await quote.to_dict()
    },
    status_code=200,
  )


@requires_auth
@uses_user
async def create_quote(request: Request, user: User):
  """Create a new Quote.
  """

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
    quote = await Quote.create(body=body, author_id=user.user_id)
  except ValidationError as e:
    return JSONResponse(
      {
        "message": "Invalid body failed validation.",
        "data": str(e)
      },
      status_code=400,
    )

  return JSONResponse(
    {
      "message": "Success.",
      "data": await quote.to_dict()
    },
    status_code=201,
  )


@requires_auth
@uses_user
async def get_all_meanings(request: Request, user: User):
  """Get all Meanings for a Quote.
  """

  quote_id = request.path_params["quote_id"]

  quote: Quote = await Quote.filter(id=quote_id).first()

  if not quote:
    return JSONResponse(
      {"message": "Quote does not exist."},
      status_code=404,
    )

  if quote.author_id != user.user_id:
    return JSONResponse(
      {
        "message":
          "Only the author is permitted to see Meanings for this Quote."
      },
      status_code=403,
    )

  meanings = await Meaning.filter(quote=quote)

  return JSONResponse(
    {
      "message": "Success.",
      "data": [(await meaning.to_dict()) for meaning in meanings]
    },
    status_code=200,
  )


@requires_auth
@uses_user
@uses_redis
async def create_meaning(request: Request, redis: Redis, user: User):
  """Create a new Meaning for a Quote.
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
      status_code=403,
    )
  
  friends = await redis.sismember(f"friends:{user.user_id}", quote.author_id)
  ballot = await redis.sscan(f"today:{day}:request:{user.user_id}")
  on_ballot = quote_id in ballot

  if not friends or not on_ballot:
    return JSONResponse({
      "message": "You are not permitted to create a Meaning for this Quote."
    }, status_code=403)

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
  except ValidationError as e:
    return JSONResponse(
      {
        "message": "Invalid body failed validation.",
        "data": str(e)
      },
      status_code=400,
    )

  return JSONResponse(
    {
      "message": "Success.",
      "data": await meaning.to_dict()
    },
    status_code=201,
  )


@requires_auth
@uses_user
async def disown_quote(request: Request, user: User):
  """Disassociate yourself with a quote.
  """

  quote_id = request.path_params["quote_id"]

  quote: Quote = await Quote.filter(id=quote_id).first()

  if not quote:
    return JSONResponse(
      {"message": "Quote does not exist."},
      status_code=404,
    )

  if quote.author_id != user.user_id:
    return JSONResponse(
      {"message": "You cannot disown a Quote that is not yours."},
      status_code=403,
    )

  quote.author_id = None
  await quote.save()

  return JSONResponse(
    {"message": "Success."},
    status_code=200,
  )
