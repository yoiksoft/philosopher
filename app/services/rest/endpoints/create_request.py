"""Endpoint to create a request to be friends with a user.
"""

from starlette.requests import Request
from starlette.responses import JSONResponse

from app.utils.auth import requires_auth, uses_user, User, get_user_by_nickname
from app.services.rest import dau


@requires_auth
@uses_user
async def handler(request: Request, user: User) -> JSONResponse:
  """Handler to create a request to be friends with a user.
  """

  requester_nickname = request.path_params["requester"]
  requester = await get_user_by_nickname(requester_nickname)

  if not requester:
    return JSONResponse({"message": "Invalid requester ID."}, status_code=400)

  if user.user_id != requester.user_id:
    return JSONResponse(
      {"message": "You cannot send a friend request on someone elses behalf."},
      status_code=403,
    )

  author_nickname = request.path_params["author"]
  author = await get_user_by_nickname(author_nickname)

  if not author:
    return JSONResponse({"message": "Author not found."}, status_code=404)

  if requester.user_id == author.user_id:
    return JSONResponse(
      {"message": "You cannot create a request to yourself."},
      status_code=400,
    )

  are_friends = await dau.are_friends(requester.user_id, author.user_id)
  if are_friends:
    return JSONResponse(
      {"message": "You are already friends."},
      status_code=400,
    )

  did_request = await dau.has_requested(author.user_id, requester.user_id)
  if did_request:
    # Make friends.
    await dau.make_friends(requester.user_id, author.user_id)

    return JSONResponse(
      {"message": "Both have requested and thus are now friends."},
      status_code=201,
    )

  await dau.make_request(requester.user_id, author.user_id)

  return JSONResponse(
    {"message": "Success."},
    status_code=200,
  )
