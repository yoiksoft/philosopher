"""Author related endpoints.
"""

import typing
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.utils.auth import get_user, use_user
from app.models import Meaning, Quote


async def get_author(request: Request) -> JSONResponse:
  """Get an author profile.
  """

  username = request.path_params["username"]
  author = await get_user(username=username)

  if not author:
    return JSONResponse(
      {
        "message": "Not found.",
      },
      status_code=404,
    )

  return JSONResponse(
    {
      "message": "Success.",
      "result": {
        "author": author,
      },
    },
    status_code=200,
  )


# GET ALL
async def get_quotes_from_author(request: Request) -> JSONResponse:
  """Get quotes from an author.
  """

  username = request.path_params["username"]
  author = await get_user(username=username)

  if not author:
    return JSONResponse(
      {
        "message": "Not found.",
      },
      status_code=404,
    )

  offset = int(request.query_params.get("offset", default=0))
  count = int(request.query_params.get("count", default=10))

  if offset < 0:
    return JSONResponse(
      {
        "message": "Query parameter 'offset' must be greater than " \
                   "or equal to 0.",
      },
      status_code=400,
    )

  if count < 1:
    return JSONResponse(
      {
        "message": "Query parameter 'count' must be greater than 1.",
      },
      status_code=400,
    )

  quotes: typing.Iterable[Quote] = await Quote \
    .filter(author=author["user_id"]) \
    .offset(offset) \
    .limit(count)

  return JSONResponse(
    {
      "message": "Success.",
      "result": [dict(quote) for quote in quotes],
    },
    status_code=200,
  )


# GET ALL
@use_user
async def get_meanings_from_author(
  request: Request,
  user: dict,
) -> JSONResponse:
  """Get all meanings from an author.
  """

  username = request.path_params["username"]
  author = await get_user(username=username)

  if not author:
    return JSONResponse(
      {
        "message": "Author not found.",
      },
      status_code=404,
    )

  if user["user_id"] != author["user_id"]:
    return JSONResponse(
      {
        "message": "You are not allowed to see this authors Meanings.",
      },
      status_code=403,
    )

  offset = int(request.query_params.get("offset", default=0))
  count = int(request.query_params.get("count", default=10))

  if offset < 0:
    return JSONResponse(
      {
        "message": "Query parameter 'offset' must be greater than " \
                   "or equal to 0.",
      },
      status_code=400,
    )

  if count < 1:
    return JSONResponse(
      {
        "message": "Query parameter 'count' must be greater than 1.",
      },
      status_code=400,
    )

  meanings: typing.Iterable[Meaning] = await Meaning \
    .filter(author=author["user_id"]) \
    .offset(offset) \
    .limit(count)

  return JSONResponse(
    {
      "message": "Success.",
      "result": [dict(meaning) for meaning in meanings],
    },
    status_code=200,
  )
