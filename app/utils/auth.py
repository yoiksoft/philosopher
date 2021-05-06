import json

import aiohttp
from jose import jwt, exceptions
from starlette.responses import JSONResponse

from app.utils import config
from app.utils.redis import Redis


__client_id = config("AUTH0_CLIENT_ID")
__client_secret = config("AUTH0_CLIENT_SECRET")


class AuthenticationError(Exception):
  pass


class User:
  def __init__(self, user_id, nickname):
    self.user_id = user_id
    self.nickname = nickname
  
  def to_dict(self):
    return {
      "user_id": self.user_id,
      "nickname": self.nickname
    }


async def get_management_token():
  """Get management token to use the Auth0 Management API.
  """

  redis = Redis().connection

  # Check for cached token in Redis.
  token = await redis.get("philosopher:token")
  # If no cache, fetch new.
  if not token:

    # Send the request for a new token.
    session = aiohttp.ClientSession(headers={
      "Content-Type": "application/json"
    })
    response = await session.post(
      f"https://kwot.us.auth0.com/oauth/token",
      data=json.dumps({
        "client_id": __client_id,
        "client_secret": __client_secret,
        "audience": "https://kwot.us.auth0.com/api/v2/",
        "grant_type": "client_credentials"
      })
    )
    token_data = await response.json()
    await session.close()

    # Store the token data.
    token = token_data["access_token"]
    expires_in = token_data["expires_in"]
    await redis.set("philosopher:token", token, expire=expires_in)
    
  # Return token.
  return token


def uses_user(func):
  """Wrapper that sends off rich user data to the underlying endpoint.
  """
  async def inner(request, *args, **kwargs):
    try:
      user_data = await get_user(request.state.user["sub"])
    except AttributeError:
      raise AuthenticationError("Endpoint must require authentication before attempting to access underlying request user.")
    return await func(request, *args, user=user_data, **kwargs)
  return inner


async def get_user(user_id):
  """Get rich user data by user ID.
  """

  token = await get_management_token()
  fields_string = ",".join(["user_id", "nickname"])

  session = aiohttp.ClientSession(headers={"Authorization": f"Bearer {token}"})
  response = await session.get(f"https://kwot.us.auth0.com/api/v2/users/{user_id}?fields={fields_string}&include_fields=true")
  user_data = await response.json()
  await session.close()
  user = User(user_data["user_id"], user_data["nickname"])

  return user


def find_matching_key(kid, keys):
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


async def get_keys(from_cache=True):
  """Fetch keys from cache and/or from JWKS endpoint.
  """

  redis = Redis().connection

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
    response = await session.get("https://kwot.us.auth0.com/.well-known/jwks.json")
    jwks = await response.json()
    await session.close()
    # Cache the keys for maximum one day.
    await redis.set("philosopher:jwks", json.dumps(jwks), expire=86400)

  return jwks


def requires_auth(func):
  """Decorator that prepends auth functionality to an endpoint.
  """

  async def inner(request, *args, **kwargs):
    """Auth wrapper
    """

    # Get the Authorization header.
    header = request.headers.get('Authorization')

    # Return an error if there is no Authorization header.
    if not header:
      return JSONResponse({
        "message": "Missing Authorization header."
      }, status_code=401)

    # Return an error if the token is not of Bearer type.
    if not header.startswith("Bearer "):
      return JSONResponse({
        "message": "Malformed Authorization header."
      }, status_code=400)

    token = header[7:]

    # Fetch keys from JSON Web Key Set.
    jwks = await get_keys(from_cache=True)
    
    # Get the token header without verifying it.
    try:
      unverified_header = jwt.get_unverified_header(token)
    except exceptions.JWTError:
      return JSONResponse({
        "message": "Error decoding authorization token headers"
      }, status_code=400)

    # For every key that our issuer has signed with previously...
    rsa_key = find_matching_key(unverified_header["kid"], jwks["keys"])

    # Return error if there's no matching signing key.
    if not rsa_key:
      # Get a fresh set of keys just in case we just missed a new sign.
      jwks = await get_keys(from_cache=False)
      # Attempt to find key again.
      rsa_key = find_matching_key(unverified_header["kid"], jwks["keys"])
      # If we still don't have a matching key.
      if not rsa_key:
        # Return an error.
        return JSONResponse({
          "message": "Invalid authorization token."
        }, status_code=401)

    # Attempt to validate and parse out user data from the token.
    user = None
    try:
      # Decode the token using the key.
      user = jwt.decode(
        token,
        rsa_key,
        algorithms=["RS256"],
        audience="philosopher",
        issuer="https://kwot.us.auth0.com/"
      )
    except jwt.ExpiredSignatureError:
      # Return error if the token expired.
      return JSONResponse({
        "message": "Authorization token is expired"
      }, status_code=401)
    except jwt.JWTClaimsError:
      # Return error if the claims are missing or invalid.
      return JSONResponse({
        "message": "Incorrect claims in authorization token"
      }, status_code=401)
    except Exception:
      # Return error if anything else went wrong.
      return JSONResponse({
        "Unable to parse authorization token."
      }, status_code=401)

    # Bind the user to the request state.
    request.state.user = user

    # Run the underlying endpoint.
    return await func(request, *args, **kwargs)
  
  # Return the wrapped endpoint.
  return inner
