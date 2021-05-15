"""Endpoint to accept a request to be friends.
"""

from starlette.requests import Request
from starlette.responses import JSONResponse

from app.utils.auth import requires_auth, uses_user, User, get_user_by_nickname
from app.services.rest import dau


@requires_auth
@uses_user
async def handler(request: Request, user: User) -> JSONResponse:
  """Handler to accept a request to be friends.
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

  try:
    request_body = await request.json()
  except:
    return JSONResponse(
      {"message": "Missing request body."},
      status_code=400,
    )

  try:
    requester_id = request_body["request_id"]
  except KeyError:
    return JSONResponse(
      {"message": "Missing value for request_id in request body."},
      status_code=400,
    )

  if author.user_id == requester_id:
    return JSONResponse(
      {"message": "You cannot be friends with yourself."},
      status_code=400,
    )

  did_request = await dau.has_requested(requester_id, user.user_id)
  if not did_request:
    return JSONResponse(
      {"message": "The specified user has not sent you a friend request."},
      status_code=400,
    )

  await dau.make_friends(requester_id, user.user_id)

  return JSONResponse(
    {"message": "Success."},
    status_code=200,
  )
