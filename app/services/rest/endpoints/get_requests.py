"""Endpoint to get all friend requests of an author.
"""

from starlette.requests import Request
from starlette.responses import JSONResponse

from app.utils.auth import requires_auth, uses_user, User, get_user, get_user_by_nickname
from app.services.rest import dau


@requires_auth
@uses_user
async def handler(request: Request, user: User) -> JSONResponse:
  """Handler to get all friend requests of an author.
  """

  author_nickname = request.path_params["author"]
  author = await get_user_by_nickname(author_nickname)

  if not author:
    return JSONResponse({"message": "Author not found."}, status_code=404)

  if user.user_id != author.user_id:
    return JSONResponse(
      {"message": "You are not allowed to view this users requests."},
      status_code=403,
    )

  requester_ids = await dau.get_requests(author.user_id)
  requesters = []
  for requester_id in requester_ids:
    requester = await get_user(requester_id)
    requesters.append(requester.to_dict())

  return JSONResponse(
    {
      "message": "Success.",
      "data": requesters
    },
    status_code=200,
  )
