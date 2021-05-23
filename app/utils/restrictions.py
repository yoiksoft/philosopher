"""Restrictions for endpoints.
"""

import typing

from app.models import Meaning, Quote


class MissingArgumentsError(Exception):
  """Error to throw when a required argument is missing from kwargs.
  """


def author_is_self(*_args, **kwargs) -> bool:
  """Checks that the author in path is the user making the request.
  """

  author: dict = kwargs.get("author")
  user: dict = kwargs.get("user")

  if not author or not user:
    raise MissingArgumentsError

  return user["user_id"] == author["user_id"]


def author_of_quote(*_args, **kwargs) -> bool:
  """Checks if the user is the author of the quote.
  """

  user: dict = kwargs.get("user")
  resource: typing.Union[Quote, Meaning] = kwargs.get("quote") \
                                        or kwargs.get("meaning")

  if not user or not resource:
    raise MissingArgumentsError

  if isinstance(resource, Quote):
    return resource.author == user["user_id"]
  if isinstance(resource, Meaning):
    return resource.quote.author == user["user_id"]
  return False


def author_of_meaning(*_args, **kwargs) -> bool:
  """Checks if the user is the author of the meaning.
  """

  user: dict = kwargs.get("user")
  meaning: Meaning = kwargs.get("meaning")

  if not user or not meaning:
    raise MissingArgumentsError

  return meaning.author == user["user_id"]
