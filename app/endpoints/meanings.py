"""Meaning related endpoints.
"""

from starlette.requests import Request
from starlette.responses import JSONResponse

from app.utils.auth import use_user
from app.schemas import MeaningSchema
from app.models import Meaning, Quote


# GET ONE
@use_user
async def get_meaning(
  request: Request,
  user: dict,
) -> JSONResponse:
  """Get a specific Meaning.
  """

  meaning_id = request.path_params["meaning_id"]
  meaning = await Meaning.get_or_none(pk=meaning_id)

  if not meaning:
    return JSONResponse(
      {
        "message": "Meaning not found.",
      },
      status_code=404,
    )

  await meaning.fetch_related("quote")

  if meaning.author != user["user_id"] \
  and meaning.quote.author != user["user_id"]:
    return JSONResponse(
      {
        "message": "You are not allowed to see this meaning.",
      },
      status_code=403,
    )

  return JSONResponse(
    {
      "message": "Success.",
      "result": await meaning.to_dict(),
    },
    status_code=200,
  )


# CREATE
@use_user
async def create_meaning(
  request: Request,
  user: dict,
) -> JSONResponse:
  """Endpoint to create a new Meaning.
  """

  try:
    data = await request.json()
  except:
    return JSONResponse(
      {
        "message": "Missing or invalid request body.",
      },
      status_code=400,
    )

  meaning_data, errors = MeaningSchema.validate_or_error(data)

  if errors:
    return JSONResponse(
      {
        "message": "Failed validation.",
        "result": dict(errors),
      },
      status_code=400,
    )

  quote_id = request.path_params["quote_id"]
  quote = await Quote.get_or_none(pk=quote_id)

  if not quote:
    return JSONResponse(
      {
        "message": "Quote not found.",
      },
      status_code=404,
    )

  if quote.author == user["user_id"]:
    return JSONResponse(
      {
        "message": "You cannot write Meanings for your own Quote.",
      },
      status_code=403,
    )

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
    body=meaning_data.body,
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
async def disown_meaning(
  request: Request,
  user: dict,
) -> JSONResponse:
  """Endpoint to disown a Meaning.
  """

  meaning_id = request.path_params["meaning_id"]
  meaning = await Meaning.get_or_none(pk=meaning_id)

  if not meaning:
    return JSONResponse(
      {
        "message": "Meaning could not be found.",
      },
      status_code=404,
    )

  if meaning.author != user["user_id"]:
    return JSONResponse(
      {
        "message": "You can only disown your own Meanings.",
      },
      status_code=403,
    )

  meaning.author = None
  await meaning.save()

  return JSONResponse(
    {
      "message": "Success.",
    },
    status_code=200,
  )
