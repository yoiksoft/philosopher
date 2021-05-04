"""Authentication and authorization related functions and routes
"""

import json
import aiohttp
from jose import jwt, exceptions
from starlette.responses import JSONResponse


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


async def get_keys(redis, from_cache=True):
  """Fetch keys from cache and/or from JWKS endpoint.
  """

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

  async def inner(request):
    """Auth wrapper
    """

    # Alias the Redis connection.
    redis = request.app.state.redis

    # Get the Authorization header.
    header = request.headers.get('Authorization')

    # Return an error if there is no Authorization header.
    if not header:
      return JSONResponse({
        "message": "Malformed Authorization header."
      }, status_code=400)

    # Return an error if the token is not of Bearer type.
    if not header.startswith("Bearer "):
      return JSONResponse({
        "message": "Malformed Authorization header."
      }, status_code=400)

    token = header[7:]

    # Fetch keys from JSON Web Key Set.
    jwks = await get_keys(redis, from_cache=True)
    
    # Get the token header without verifying it.
    try:
      unverified_header = jwt.get_unverified_header(token)
    except exceptions.JWTError:
      return JSONResponse({
        "message": "Error decoding token headers"
      }, status_code=400)

    # For every key that our issuer has signed with previously...
    rsa_key = find_matching_key(unverified_header["kid"], jwks["keys"])

    # Return error if there's no matching signing key.
    if not rsa_key:
      # Get a fresh set of keys just in case we just missed a new sign.
      jwks = await get_keys(redis, from_cache=False)
      # Attempt to find key again.
      rsa_key = find_matching_key(unverified_header["kid"], jwks["keys"])
      # If we still don't have a matching key.
      if not rsa_key:
        # Return an error.
        return JSONResponse({
          "message": "Invalid Token."
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
        "message": "Token is expired"
      }, status_code=401)
    except jwt.JWTClaimsError:
      # Return error if the claims are missing or invalid.
      return JSONResponse({
        "message": "Incorrect claims in token"
      }, status_code=401)
    except Exception:
      # Return error if anything else went wrong.
      return JSONResponse({
        "Unable to parse authentication token."
      }, status_code=401)

    # Bind the user to the request state.
    request.state.user = user

    # Run the underlying endpoint.
    return await func(request)
  
  # Return the wrapped endpoint.
  return inner
