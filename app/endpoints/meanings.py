"""Meaning related endpoints.
"""

from starlette.requests import Request
from starlette.responses import JSONResponse

from app.utils.decorators import (
  restrict_meaning_author_quote_author,
  restrict_meaning_author,
  restrict_quote_not_author,
  use_json_body,
  use_user,
  use_path_meaning,
  use_path_quote,
)
from app.schemas import MeaningSchema
from app.models import Meaning, Quote


# GET ONE
@use_user
@use_path_meaning(path_key="meaning_id")
@restrict_meaning_author_quote_author
async def get_meaning(
  _request: Request,
  meaning: Meaning,
  *_args,
  **_kwargs,
) -> JSONResponse:
  """Get a specific Meaning.
  """

  return JSONResponse(
    {
      "message": "Success.",
      "result": await meaning.to_dict(),
    },
    status_code=200,
  )


# CREATE
@use_json_body(MeaningSchema)
@use_path_quote(path_key="quote_id")
@use_user
@restrict_quote_not_author
async def create_meaning(
  _request: Request,
  user: dict,
  quote: Quote,
  data: MeaningSchema,
  *_args,
  **_kwargs,
) -> JSONResponse:
  """Endpoint to create a new Meaning.
  """

  meaning = await Meaning.get_or_none(
    author=user["user_id"],
    quote=quote,
  )

  if meaning:
    return JSONResponse(
      {
        "message": "You have already submitted a Meaning for this Quote.",
      },
      status_code=403,
    )

  meaning = await Meaning.create(
    author=user["user_id"],
    body=data.body,
    quote=quote,
  )

  return JSONResponse(
    {
      "message": "Success.",
      "result": await meaning.to_dict(),
    },
    status_code=201,
  )


# DELETE
@use_user
@use_path_meaning(path_key="meaning_id")
@restrict_meaning_author
async def disown_meaning(
  _request: Request,
  meaning: Meaning,
  *_args,
  **_kwargs,
) -> JSONResponse:
  """Endpoint to disown a Meaning.
  """

  meaning.author = None
  await meaning.save()

  return JSONResponse(
    {
      "message": "Success.",
    },
    status_code=200,
  )
