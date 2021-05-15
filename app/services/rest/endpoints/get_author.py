"""Endpoint to get a specific author.
"""

from starlette.requests import Request
from starlette.responses import JSONResponse

from app.utils.auth import requires_auth, get_user_by_nickname


@requires_auth
async def handler(request: Request) -> JSONResponse:
  """Handler to get a specific author.
  """

  author_nickname = request.path_params["author"]
  author = await get_user_by_nickname(author_nickname)

  if not author:
    return JSONResponse(
      {"message": "Author not found."},
      status_code=404,
    )

  return JSONResponse(
    {
      "message": "Success.",
      "data": author.to_dict()
    },
    status_code=200,
  )
