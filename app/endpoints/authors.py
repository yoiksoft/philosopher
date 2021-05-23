"""Author related endpoints.
"""

import typing
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.utils.decorators import path_author_is_self, use_user, use_path_author
from app.models import Meaning, Quote


@use_path_author(path_key="username")
async def get_author(
  _request: Request,
  author: dict,
  *_args,
  **_kwargs,
) -> JSONResponse:
  """Get an author profile.
  """

  return JSONResponse(
    {
      "message": "Success.",
      "result": {
        "author": author,
      },
    },
    status_code=200,
  )


@use_path_author(path_key="username")
async def get_quotes_from_author(
  request: Request,
  author: dict,
  *_args,
  **_kwargs,
) -> JSONResponse:
  """Get quotes from an author.
  """

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
      "result": [await quote.to_dict() for quote in quotes],
    },
    status_code=200,
  )


# GET ALL
@use_user
@use_path_author(path_key="username")
@path_author_is_self
async def get_meanings_from_author(
  request: Request,
  author: dict,
  *_args,
  **_kwargs,
) -> JSONResponse:
  """Get all meanings from an author.
  """

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
