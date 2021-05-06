from aioredis import Redis
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.utils.redis import uses_redis
from app.utils.auth import requires_auth, uses_user, User, get_user


@uses_redis
@requires_auth
@uses_user
async def get_friends(request: Request, redis: Redis, user: User):
  """Get all friends of a user.

  Can be queried by anyone.
  """

  user_id = request.path_params["user_id"]

  are_friends = await redis.sismember(f"friends:{user_id}", user.user_id)
  if not are_friends and user_id != user.user_id:
    return JSONResponse({
      "message": "You are not friends with this user."
    }, status_code=403)

  friends_ids = []
  cursor = "0"
  while cursor != 0:
    cursor, data = await redis.sscan(f"friends:{user_id}", cursor=cursor)
    friends_ids.extend(data)

  friends = []
  for friend_id in friends_ids:
    friend = await get_user(friend_id)
    friends.append(friend.to_dict())

  return JSONResponse({
    "message": f"Success.",
    "data": friends
  }, status_code=200)


@uses_redis
@requires_auth
@uses_user
async def accept_request(request: Request, redis: Redis, user: User):
  """Accept a request to be friends.

  Restricted to the recipient of the request.
  """

  user_id = request.path_params["user_id"]

  if user.user_id != user_id:
    return JSONResponse({
      "message": "You are not allowed to perform this action."
    }, status_code=403)

  try:
    request_body = await request.json()
  except:
    return JSONResponse({
      "message": "Missing request body."
    }, status_code=400)
  
  requester_id = request_body["request_id"]

  did_request = await redis.sismember(f"requests:{user_id}", requester_id)
  if not did_request:
    return JSONResponse({
      "message": "The specified user has not sent you a friend request."
    }, status_code=400)
  
  await redis.smove(f"requests:{user_id}", f"friends:{user_id}", requester_id)
  await redis.sadd(f"friends:{requester_id}", user_id)

  return JSONResponse({
    "message": "Success."
  }, status_code=200)


@uses_redis
@requires_auth
@uses_user
async def remove_friend(request: Request, redis: Redis, user: User):
  """Remove an existing friend.

  Restricted to the recipient of the request.
  """

  user_id = request.path_params["user_id"]

  if user.user_id != user_id:
    return JSONResponse({
      "message": "You are not allowed to perform this action."
    }, status_code=403)
  
  friend_id = request.path_params["friend_id"]

  is_friend = await redis.sismember(f"friends:{user_id}", friend_id)
  if not is_friend:
    return JSONResponse({
      "message": "The specified user is not your friend."
    }, status_code=400)
  
  await redis.srem(f"friends:{user_id}", friend_id)
  await redis.srem(f"friends:{friend_id}", user_id)

  return JSONResponse({
    "message": "Success."
  }, status_code=200)


@uses_redis
@requires_auth
@uses_user
async def get_requests(request: Request, redis: Redis, user: User):
  """Get all friend requests of a user.

  Only shows logged in users requests.
  """

  user_id = request.path_params["user_id"]

  if user.user_id != user_id:
    return JSONResponse({
      "message": "You are not allowed to view this users requests."
    }, status_code=403)

  requester_ids = []
  cursor = "0"
  while cursor != 0:
    cursor, data = await redis.sscan(f"requests:{user_id}", cursor=cursor)
    requester_ids.extend(data)

  requesters = []
  for requester_id in requester_ids:
    requester = await get_user(requester_id)
    requesters.append(requester.to_dict())

  return JSONResponse({
    "message": f"Success.",
    "data": requesters
  }, status_code=200)


@uses_redis
@requires_auth
@uses_user
async def create_request(request: Request, redis: Redis, user: User):
  """Create a request to be friends with a user.

  Anyone can run this.
  """

  requester_id = request.path_params["request_id"]

  if user.user_id != requester_id:
    return JSONResponse({
      "message": "You cannot send a friend request on someone elses behalf."
    }, status_code=403)

  recipient_id = request.path_params["user_id"]

  if requester_id == recipient_id:
    return JSONResponse({
      "message": "You cannot create a request to yourself"
    }, status_code=400)
  
  are_friends = await redis.sismember(f"friends:{recipient_id}", requester_id)
  if are_friends:
    return JSONResponse({
      "message": "You are already friends."
    }, status_code=400)
  
  # If the person requesting has recieved a request from the recipient...
  did_request = await redis.sismember(f"requests:{requester_id}", recipient_id)
  if did_request:
    # ...make friends
    await redis.smove(f"requests:{requester_id}", f"friends:{requester_id}", recipient_id)
    await redis.sadd(f"friends:{recipient_id}", requester_id)
    return JSONResponse({
      "message": "Both have requested and thus are now friends."
    }, status_code=201)
  
  await redis.sadd(f"requests:{recipient_id}", requester_id)

  return JSONResponse({
    "message": "Success."
  }, status_code=200)


@uses_redis
@requires_auth
@uses_user
async def delete_request(request: Request, redis: Redis, user: User):
  """Decline a request to be friends.

  Restricted to the recipient of the request.
  """

  user_id = request.path_params["user_id"]  

  if user.user_id != user_id:
    return JSONResponse({
      "message": "You cannot decline a friend request on someone elses behalf."
    }, status_code=403)

  requester_id = request.path_params["request_id"]

  has_requested = await redis.sismember(f"requests:{user_id}", requester_id)
  if not has_requested:
    return JSONResponse({
      "message": "You do not have a friend request from this user."
    }, status_code=400)
  
  await redis.srem(f"requests:{user_id}", requester_id)

  return JSONResponse({
    "message": "Success."
  }, status_code=200)
