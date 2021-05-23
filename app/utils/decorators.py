"""Endpoint decorators.
"""

import typing
from functools import wraps

from starlette.requests import Request
from starlette.responses import JSONResponse
from tortoise.models import Model
from typesystem.schemas import Schema

from app.models import Author, Meaning
from app.utils import auth


def use_user(func: typing.Coroutine) -> typing.Coroutine:
  """Wrapper that sends off rich user data to the underlying endpoint.
  """

  async def inner(request: Request, *args, **kwargs):
    # Grab Auth0 ID from request state.
    user_id = request.state.user["sub"]
    # Get user profile information.
    user = await auth.get_user(user_id=user_id)
    # Run the underlying endpoint, passing down the user.
    return await func(request, *args, user=user, **kwargs)

  return inner


def use_path_model(model: Model, path_key: str = "model_id"):
  """Wrapper that exposes a model from request path.
  """

  def wrapper(func: typing.Coroutine):

    @wraps(func)
    async def wrapped(request: Request, *args, **kwargs):
      instance_pk = request.path_params[path_key]

      if issubclass(model, Model):
        instance = await model.get_or_none(pk=instance_pk)
      elif model is Author:
        instance = await auth.get_user(username=instance_pk)
      else:
        instance = None

      if not instance:
        return JSONResponse(
          {
            "message": "Not found.",
          },
          status_code=404,
        )
      if isinstance(instance, Meaning):
        await instance.fetch_related("quote")
      key: str = instance.__class__.__name__.lower()
      kwargs[key] = instance
      return await func(request, *args, **kwargs)

    return wrapped

  return wrapper


def restrict(*check_functions: typing.Iterable[typing.Callable[..., bool]],
             assertion: bool = True) -> typing.Callable:
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
