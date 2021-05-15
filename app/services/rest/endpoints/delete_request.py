"""Endpoint to decline a request to be friends.
"""

from starlette.requests import Request
from starlette.responses import JSONResponse

from app.utils.auth import requires_auth, uses_user, User, get_user_by_nickname
from app.services.rest import dau


@requires_auth
@uses_user
async def handler(request: Request, user: User) -> JSONResponse:
  """Handler to decline a request to be friends.
  """

  author_nickname = request.path_params["author"]
  author = await get_user_by_nickname(author_nickname)

  if not author:
    return JSONResponse({"message": "Author not found."}, status_code=404)

  if user.user_id != author.user_id:
    return JSONResponse(
      {
        "message":
          "You cannot decline a friend request on someone elses behalf."
      },
      status_code=403,
    )

  requester_nickname = request.path_params["requester"]
  requester = await get_user_by_nickname(requester_nickname)

  if not requester:
    return JSONResponse({"message": "Invalid requester ID."}, status_code=400)

  has_requested = await dau.has_requested(requester.user_id, author.user_id)
  if not has_requested:
    return JSONResponse(
      {"message": "You do not have a friend request from this user."},
      status_code=400,
    )

  await dau.remove_request(requester.user_id, author.user_id)

  return JSONResponse(
    {"message": "Success."},
    status_code=200,
  )
