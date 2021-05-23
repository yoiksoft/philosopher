"""Authorization utilities
"""

import json
import typing

import aiohttp
from aioredis import Redis
from jose import jwt, exceptions
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.utils import config
from app.utils.redis import Redis as RedisPool

_BASE_URL = config("AUTH0_BASE_URL")
_CLIENT_ID = config("AUTH0_CLIENT_ID")
_CLIENT_SECRET = config("AUTH0_CLIENT_SECRET")
_ALGORITHMS = ["RS256"]
_AUDIENCE = config("AUTH0_AUTH_AUDIENCE", default="philosopher")


async def __get_management_token() -> str:
  """Get management token to use the Auth0 Management API.
  """

  redis: Redis = RedisPool().connection

  # Check for cached token in Redis.
  token = await redis.get("philosopher:token")
  # If no cache, fetch new.
  if not token:

    # Send the request for a new token.
    session = aiohttp.ClientSession(
      headers={"Content-Type": "application/json"})
    response = await session.post(
      f"https://{_BASE_URL}/oauth/token",
      data=json.dumps({
        "client_id": _CLIENT_ID,
        "client_secret": _CLIENT_SECRET,
        "audience": f"https://{_BASE_URL}/api/v2/",
        "grant_type": "client_credentials"
      }))
    token_data = await response.json()
    await session.close()

    # Store the token data.
    token = token_data["access_token"]
    expires_in = token_data["expires_in"]
    await redis.set("philosopher:token", token, expire=expires_in)

  # Return token.
  return token


async def __get_user_identifier(
  user_id: str = None,
  username: str = None,
) -> str:
  """Get username from user ID.
  """

  if user_id and username:
    raise ValueError("Must specify one of 'user_id' or 'username', not both")

  redis: Redis = RedisPool().connection

  if username:
    field_had = "username"
    value_had = username
    field_wanted = "user_id"

  elif user_id:
    field_had = "user_id"
    value_had = user_id
    field_wanted = "username"

  # Fetch username from cache.
  value_wanted = await redis.get(f"{field_wanted}:{value_had}")

  # Fetch fresh username if we don't have any in cache.
  if not value_wanted:
    token = await __get_management_token()

    session = aiohttp.ClientSession(
      headers={"Authorization": f"Bearer {token}"})
    response = await session.get(
      f"https://{_BASE_URL}/api/v2/users" \
      f"?q={field_had}:\"{value_had}\"" \
      f"&fields={field_wanted}" \
       "&include_fields=true")
    result = await response.json()
    try:
      user_data = result.pop()
    except IndexError:
      await session.close()
      return None
    await session.close()
    value_wanted = user_data[field_wanted]

    # Cache username indefinitely.
    await redis.set(f"{field_wanted}:{value_had}", value_wanted)

  # Return the username.
  return value_wanted


async def get_user(
  user_id: str = None,
  username: str = None,
) -> dict:
  """Get rich user data by user ID.
  """

  if username:
    user_id = await __get_user_identifier(username=username)
    if not user_id:
      return None

  redis: Redis = RedisPool().connection

  # Fetch user data from cache.
  user_data = await redis.hgetall(f"userdata:{user_id}")

  # Fetch fresh data if we don't have any in cache.
  if not user_data:
    token = await __get_management_token()
    fields_string = ",".join(["user_id", "username", "picture"])

    session = aiohttp.ClientSession(
      headers={"Authorization": f"Bearer {token}"})
    response = await session.get(
      f"https://{_BASE_URL}/api/v2/users/{user_id}" \
      f"?fields={fields_string}" \
       "&include_fields=true")
    user_data = await response.json()
    await session.close()

    # Cache user profile data for 10 minutes.
    await redis.hmset_dict(f"userdata:{user_id}", user_data)
    await redis.expire(f"userdata:{user_id}", 600)

  # Return the user data.
  return user_data


def _find_matching_key(kid: str, keys: typing.List[dict]) -> dict:
  """Find matching key for a specific key ID.
  """

  rsa_key = {}
  for key in keys:
    # If the issuer key ID matches the unverified header key ID.
    if key["kid"] == kid:
      # Assume that's the right key and store key data.
      rsa_key = {
        "kty": key["kty"],
        "kid": key["kid"],
        "use": key["use"],
        "n": key["n"],
        "e": key["e"]
      }

  return rsa_key


async def _get_keys(from_cache: bool = True) -> dict:
  """Fetch keys from cache and/or from JWKS endpoint.
  """

  redis: Redis = RedisPool().connection

  keys_raw = None
  jwks = None
  if from_cache:
    # Get from cache
    keys_raw = await redis.get("philosopher:jwks")
  if keys_raw:
    # Parse to JSON.
    jwks = json.loads(keys_raw)
  else:
    # Get a fresh set of keys.
    session = aiohttp.ClientSession()
    response = await session.get(f"https://{_BASE_URL}/.well-known/jwks.json")
    jwks = await response.json()
    await session.close()
    # Cache the keys for maximum one day.
    await redis.set("philosopher:jwks", json.dumps(jwks), expire=86400)

  return jwks


class AuthMiddleware(BaseHTTPMiddleware):
  """Ensures that clients are authorized before accessing routes.
  """

  async def dispatch(
    self,
    request: Request,
    call_next: typing.Callable,
  ) -> Response:
    """Code to run when the middleware is dispatched.
    """

    # Get the Authorization header.
    header = request.headers.get('Authorization')

    # Return an error if there is no Authorization header.
    if not header:
      return JSONResponse(
        {"message": "Missing Authorization header."},
        status_code=401,
      )

    # Return an error if the token is not of Bearer type.
    if not header.startswith("Bearer "):
      return JSONResponse(
        {"message": "Malformed Authorization header."},
        status_code=400,
      )

    token = header[7:]

    # Fetch keys from JSON Web Key Set.
    jwks = await _get_keys(from_cache=True)

    # Get the token header without verifying it.
    try:
      unverified_header = jwt.get_unverified_header(token)
    except exceptions.JWTError:
      return JSONResponse(
        {"message": "Error decoding authorization token headers"},
        status_code=400,
      )

    # For every key that our issuer has signed with previously...
    rsa_key = _find_matching_key(unverified_header["kid"], jwks["keys"])

    # Return error if there's no matching signing key.
    if not rsa_key:
      # Get a fresh set of keys just in case we just missed a new sign.
      jwks = await _get_keys(from_cache=False)
      # Attempt to find key again.
      rsa_key = _find_matching_key(unverified_header["kid"], jwks["keys"])
      # If we still don't have a matching key.
      if not rsa_key:
        # Return an error.
        return JSONResponse(
          {"message": "Invalid authorization token."},
          status_code=401,
        )

    # Attempt to validate and parse out user data from the token.
    user = None
    try:
      # Decode the token using the key.
      user = jwt.decode(
        token,
        rsa_key,
        algorithms=_ALGORITHMS,
        audience=_AUDIENCE,
        issuer=f"https://{_BASE_URL}/")
    except jwt.ExpiredSignatureError:
      # Return error if the token expired.
      return JSONResponse(
        {"message": "Authorization token is expired"},
        status_code=401,
      )
    except jwt.JWTClaimsError:
      # Return error if the claims are missing or invalid.
      return JSONResponse(
        {"message": "Incorrect claims in authorization token"},
        status_code=401,
      )
    except:
      # Return error if anything else went wrong.
      return JSONResponse(
        {"message": "Unable to parse authorization token."},
        status_code=401,
      )

    # Bind the user to the request state.
    request.state.user = user

    # Run the underlying endpoint.
    return await call_next(request)
