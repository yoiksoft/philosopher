from starlette.requests import Request
from starlette.responses import JSONResponse

from app.services.friends import dau
from app.utils.auth import requires_auth, uses_user, User, get_user


@requires_auth
@uses_user
async def get_friends(request: Request, user: User):
  """Get all friends of a user.

  Can be queried by anyone.
  """

  # Get the user ID to find friends for.
  user_id = request.path_params["user_id"]

  # Error if the requester is not friends with the specified user.
  are_friends = await dau.are_friends(user_id, user.user_id)
  if not are_friends and user_id != user.user_id:
    return JSONResponse({
      "message": "You are not friends with this user."
    }, status_code=403)

  # Get friends.
  friends_ids = await dau.get_friends(user_id)
  friends = []
  for friend_id in friends_ids:
    friend = await get_user(friend_id)
    friends.append(friend.to_dict())

  return JSONResponse({
    "message": f"Success.",
    "data": friends
  }, status_code=200)


@requires_auth
@uses_user
async def accept_request(request: Request, user: User):
  """Accept a request to be friends.

  Restricted to the recipient of the request.
  """

  # Get the user ID to accept request on behalf of.
  user_id = request.path_params["user_id"]

  # Error if not user.
  if user.user_id != user_id:
    return JSONResponse({
      "message": "You are not allowed to perform this action."
    }, status_code=403)

  # Get requester from body.
  try:
    request_body = await request.json()
  except:
    return JSONResponse({
      "message": "Missing request body."
    }, status_code=400)
  requester_id = request_body["request_id"]

  # Ensure they're not the same.
  if user_id == requester_id:
    return JSONResponse({
      "message": "You cannot be friends with yourself."
    }, status_code=400)

  # Verify that the specified user has made a request.
  did_request = await dau.has_requested(requester_id, user.user_id)
  if not did_request:
    return JSONResponse({
      "message": "The specified user has not sent you a friend request."
    }, status_code=400)
  
  # Make friends.
  await dau.make_friends(requester_id, user.user_id)

  return JSONResponse({
    "message": "Success."
  }, status_code=200)


@requires_auth
@uses_user
async def remove_friend(request: Request, user: User):
  """Remove an existing friend.

  Restricted to the recipient of the request.
  """

  # Get the users ID.
  user_id = request.path_params["user_id"]

  # Error if not user.
  if user.user_id != user_id:
    return JSONResponse({
      "message": "You are not allowed to perform this action."
    }, status_code=403)
  
  # Get the friend ID to remove.
  friend_id = request.path_params["friend_id"]

  # Verify that they are in fact friends.
  is_friend = await dau.are_friends(user_id, friend_id)
  if not is_friend:
    return JSONResponse({
      "message": "The specified user is not your friend."
    }, status_code=400)
  
  # Remove friends.
  await dau.remove_friends(user_id, friend_id)

  return JSONResponse({
    "message": "Success."
  }, status_code=200)


@requires_auth
@uses_user
async def get_requests(request: Request, user: User):
  """Get all friend requests of a user.

  Only shows logged in users requests.
  """

  # Get user ID.
  user_id = request.path_params["user_id"]

  # Error if not user.
  if user.user_id != user_id:
    return JSONResponse({
      "message": "You are not allowed to view this users requests."
    }, status_code=403)

  # Get requests.
  requester_ids = await dau.get_requests(user_id)
  requesters = []
  for requester_id in requester_ids:
    requester = await get_user(requester_id)
    requesters.append(requester.to_dict())

  return JSONResponse({
    "message": f"Success.",
    "data": requesters
  }, status_code=200)


@requires_auth
@uses_user
async def create_request(request: Request, user: User):
  """Create a request to be friends with a user.

  Anyone can run this.
  """

  # Get requester ID.
  requester_id = request.path_params["request_id"]

  # Error if not user.
  if user.user_id != requester_id:
    return JSONResponse({
      "message": "You cannot send a friend request on someone elses behalf."
    }, status_code=403)

  # Get recipient ID.
  recipient_id = request.path_params["user_id"]

  # Error if trying to friend self.
  if requester_id == recipient_id:
    return JSONResponse({
      "message": "You cannot create a request to yourself"
    }, status_code=400)
  
  # Check that the users aren't already friends.
  are_friends = await dau.are_friends(requester_id, recipient_id)
  if are_friends:
    return JSONResponse({
      "message": "You are already friends."
    }, status_code=400)
  
  # If the person requesting has recieved a request from the recipient...
  did_request = await dau.has_requested(recipient_id, requester_id)
  if did_request:
    # Make friends.
    await dau.make_friends(requester_id, recipient_id)

    return JSONResponse({
      "message": "Both have requested and thus are now friends."
    }, status_code=201)
  
  # Otherwire, make request.
  await dau.make_request(requester_id, recipient_id)

  return JSONResponse({
    "message": "Success."
  }, status_code=200)


@requires_auth
@uses_user
async def delete_request(request: Request, user: User):
  """Decline a request to be friends.

  Restricted to the recipient of the request.
  """

  # Get the user ID.
  user_id = request.path_params["user_id"]  

  # Error if not user.
  if user.user_id != user_id:
    return JSONResponse({
      "message": "You cannot decline a friend request on someone elses behalf."
    }, status_code=403)

  # Get the requester ID.
  requester_id = request.path_params["request_id"]

  # Verify that the user has requested.
  has_requested = await dau.has_requested(requester_id, user_id)
  if not has_requested:
    return JSONResponse({
      "message": "You do not have a friend request from this user."
    }, status_code=400)
  
  await dau.remove_request(requester_id, user_id)

  return JSONResponse({
    "message": "Success."
  }, status_code=200)
