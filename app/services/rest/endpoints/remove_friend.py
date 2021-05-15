"""Endpoint to remove an existing friend.
"""

from starlette.requests import Request
from starlette.responses import JSONResponse

from app.utils.auth import requires_auth, uses_user, User, get_user_by_nickname
from app.services.rest import dau


@requires_auth
@uses_user
async def handler(request: Request, user: User) -> JSONResponse:
  """Handler to remove an existing friend.
  """

  author_nickname = request.path_params["author"]
  author = await get_user_by_nickname(author_nickname)

  if not author:
    return JSONResponse({"message": "Author not found."}, status_code=404)

  if user.user_id != author.user_id:
    return JSONResponse(
      {"message": "You are not allowed to perform this action."},
      status_code=403,
    )

  friend_nickname = request.path_params["friend"]
  friend = await get_user_by_nickname(friend_nickname)

  if not friend:
    return JSONResponse({"message": "Invalid friend ID."}, status_code=400)

  is_friend = await dau.are_friends(author.user_id, friend.user_id)
  if not is_friend:
    return JSONResponse(
      {"message": "The specified user is not your friend."},
      status_code=400,
    )

  await dau.remove_friends(author.user_id, friend.user_id)

  return JSONResponse(
    {"message": "Success."},
    status_code=200,
  )
