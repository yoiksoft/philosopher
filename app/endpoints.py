"""Application endpoints.
"""

from starlette.requests import Request
from starlette.responses import JSONResponse

from app.utils.auth import use_user
from app.utils.auth import get_user
from app.models import RelationshipStatus
from app import dto


async def get_author(request: Request,) -> JSONResponse:
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


@use_user
async def get_relationship(request: Request, user: dict) -> JSONResponse:
  """Check the relationship between any user and the signed in user.
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

  if author["user_id"] == user["user_id"]:
    return JSONResponse(
      {
        "message": "Success.",
        "result": RelationshipStatus.ME,
      },
      status_code=200,
    )

  status = await dto.get_relationship_between(
    author["user_id"],
    user["user_id"],
  )

  return JSONResponse(
    {
      "message": "Success.",
      "result": status,
    },
    status_code=200,
  )


async def get_quotes(request: Request,) -> JSONResponse:
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

  quotes = await dto.get_quotes_from(
    author["user_id"],
    offset=int(offset),
    count=int(count),
  )

  return JSONResponse(
    {
      "message": "Success.",
      "result": quotes,
    },
    status_code=200,
  )
