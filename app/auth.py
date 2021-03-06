"""Authentication and authorization related functions and routes
"""

import aiohttp
from starlette.responses import JSONResponse


def requires_auth(func):
  """Decorator that prepends auth functionality to an endpoint.
  """

  async def inner(request):
    """Auth wrapper
    """

    # Get the Authorization header.
    header = request.headers.get('Authorization')

    # Return an error if there is no Authorization header.
    if not header:
      return JSONResponse({
        "message": "Missing Authorization header."
      }, status_code=400)
    
    # Return an error if the token is not of Bearer type.
    if not header.startswith("Bearer "):
      return JSONResponse({
        "message": "Malformed Authorization header."
      }, status_code=400)

    # Request user data from Discord.
    session = aiohttp.ClientSession(headers={ "Authorization": header })
    response = await session.get("https://discord.com/api/users/@me")
    user = await response.json()
    await session.close()

    # Get the user ID, to determine whether or not the request worked.
    has_id = user.get("id")

    # If the Discord request failed, then there is an issue with authentication.
    if not has_id:
      return JSONResponse({
        "message": "Failed to authenticate with Discord."
      }, status_code=401)
    
    # Bind the user to the request state.
    request.state.user = user

    # Run the underlying endpoint.
    return await func(request)
  
  # Return the wrapped endpoint.
  return inner