"""Endpoint to get all friends of an author.
"""

from starlette.requests import Request
from starlette.responses import JSONResponse

from app.utils.auth import requires_auth, uses_user, User, get_user, get_user_by_nickname
from app.services.rest import dau


@requires_auth
@uses_user
async def handler(request: Request, user: User) -> JSONResponse:
  """Handler to get all friends of an author.
  """

  author_nickname = request.path_params["author"]
  author = await get_user_by_nickname(author_nickname)

  if not author:
    return JSONResponse({"message": "Author not found."}, status_code=404)

  are_friends = await dau.are_friends(author.user_id, user.user_id)
  if not are_friends and author.user_id != user.user_id:
    return JSONResponse(
      {"message": "You are not friends with this user."},
      status_code=403,
    )

  friends_ids = await dau.get_friends(author.user_id)
  friends = []
  for friend_id in friends_ids:
    friend = await get_user(friend_id)
    friends.append(friend.to_dict())

  return JSONResponse(
    {
      "message": "Success.",
      "data": friends
    },
    status_code=200,
  )
