"""Endpoint decorators.
"""

import typing
from functools import wraps

from starlette.requests import Request
from starlette.responses import JSONResponse
from typesystem.schemas import Schema

from app.models import Meaning, Quote
from app.utils import auth


def use_user(func: typing.Coroutine) -> typing.Coroutine:
  """Wrapper that sends off rich user data to the underlying endpoint.
  """

  async def inner(request: Request, *args, **kwargs):

    # Grab Auth0 ID from request state.
    user_id = request.state.user["sub"]

    # Get user profile information.
    user_data = await auth.get_user(user_id=user_id)

    # Run the underlying endpoint, passing down the user.
    return await func(request, *args, user=user_data, **kwargs)

  return inner


def use_path_author(path_key: str = "username"):
  """Wrapper that exposes an author from request path.
  """

  def wrapper(func: typing.Coroutine):

    @wraps(func)
    async def wrapped(request: Request, *args, **kwargs):
      username = request.path_params[path_key]
      author = await auth.get_user(username=username)
      if not author:
        return JSONResponse(
          {"message": "Author not found."},
          status_code=404,
        )
      return await func(request, *args, author=author, **kwargs)

    return wrapped

  return wrapper


def use_path_meaning(path_key: str = "meaning_id"):
  """Wrapper that exposes a meaning from request path.
  """

  def wrapper(func: typing.Coroutine):

    @wraps(func)
    async def wrapped(request: Request, *args, **kwargs):
      meaning_id = request.path_params[path_key]
      meaning = await Meaning.get_or_none(pk=meaning_id)
      if not meaning:
        return JSONResponse(
          {
            "message": "Meaning not found.",
          },
          status_code=404,
        )
      await meaning.fetch_related("quote")
      return await func(request, *args, meaning=meaning, **kwargs)

    return wrapped

  return wrapper


def use_path_quote(path_key: str = "quote_id"):
  """Wrapper that exposes a quote from request path.
  """

  def wrapper(func: typing.Coroutine):

    @wraps(func)
    async def wrapped(request: Request, *args, **kwargs):
      quote_id = request.path_params[path_key]
      quote = await Quote.get_or_none(pk=quote_id)
      if not quote:
        return JSONResponse(
          {
            "message": "Quote not found.",
          },
          status_code=404,
        )
      return await func(request, *args, quote=quote, **kwargs)

    return wrapped

  return wrapper


def restrict(
  *check_functions: typing.Iterable[typing.Callable[..., bool]],
  assertion: bool = True
) -> typing.Callable:
  """Wrap an endpiont with some sort of restriction.
  """

  def wrapper(func: typing.Coroutine) -> typing.Coroutine:
    @wraps(func)
    async def wrapped(request: Request, *args, **kwargs) -> JSONResponse:
      results = [fun(*args, **kwargs) for fun in check_functions]
      if any(results) is not assertion:
        return JSONResponse(
          {
            "message": "Forbidden.",
          },
          status_code=403,
        )
      return await func(request, *args, **kwargs)
    return wrapped
  return wrapper


def validate_body(schema: Schema):
  """Wrapper that validates and exposes request body as keyword argument.
  """

  def wrapper(func: typing.Coroutine):

    @wraps(func)
    async def wrapped(request: Request, *args, **kwargs):
      try:
        data = await request.json()
      except:
        return JSONResponse(
          {
            "message": "Missing or invalid request body.",
          },
          status_code=400,
        )

      validated, errors = schema.validate_or_error(data)

      if errors:
        return JSONResponse(
          {
            "message": "Failed validation.",
            "result": dict(errors),
          },
          status_code=400,
        )

      return await func(request, *args, data=validated, **kwargs)

    return wrapped

  return wrapper
