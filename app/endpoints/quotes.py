"""Quote related endpoints.
"""

from starlette.requests import Request
from starlette.responses import JSONResponse

from app.utils.auth import use_user
from app.schemas import QuoteSchema
from app.models import Quote


# GET ONE
async def get_quote(request: Request) -> JSONResponse:
  """Get a specific Quote.
  """

  quote_id = request.path_params["quote_id"]
  quote = await Quote.get_or_none(pk=quote_id)

  if not quote:
    return JSONResponse(
      {
        "message": "Quote not found.",
      },
      status_code=404,
    )

  return JSONResponse(
    {
      "message": "Success.",
      "result": await quote.to_dict(),
    },
    status_code=200,
  )


# CREATE
@use_user
async def create_quote(
  request: Request,
  user: dict,
) -> JSONResponse:
  """Endpoint to create a new Quote.
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

  quote_data, errors = QuoteSchema.validate_or_error(data)

  if errors:
    return JSONResponse(
      {
        "message": "Failed validation.",
        "result": dict(errors),
      },
      status_code=400,
    )

  quote = await Quote.create(
    author=user["user_id"],
    body=quote_data.body,
  )

  return JSONResponse(
    {
      "message": "Success.",
      "result": await quote.to_dict()
    },
    status_code=201,
  )


# DELETE
@use_user
async def disown_quote(
  request: Request,
  user: dict,
) -> JSONResponse:
  """Endpoint to disown a Quote.
  """

  quote_id = request.path_params["quote_id"]

  quote = await Quote.get_or_none(pk=quote_id)

  if not quote:
    return JSONResponse(
      {
        "message": "Quote could not be found.",
      },
      status_code=404,
    )

  if quote.author != user["user_id"]:
    return JSONResponse(
      {
        "message": "You can only delete your own quotes.",
      },
      status_code=403,
    )

  quote.author = None
  await quote.save()

  return JSONResponse(
    {
      "message": "Success.",
    },
    status_code=200,
  )
