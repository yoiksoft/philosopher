"""Quote related endpoints.
"""

from starlette.requests import Request
from starlette.responses import JSONResponse

from app.utils.decorators import restrict_quote_author, use_json_body, use_path_quote, use_user
from app.schemas import QuoteSchema
from app.models import Quote


@use_path_quote(path_key="quote_id")
async def get_quote(
  _request: Request,
  quote: Quote,
  *_args,
  **_kwargs,
) -> JSONResponse:
  """Get a specific Quote.
  """

  return JSONResponse(
    {
      "message": "Success.",
      "result": await quote.to_dict(),
    },
    status_code=200,
  )


# CREATE
@use_json_body(QuoteSchema)
@use_user
async def create_quote(
  _request: Request,
  user: dict,
  data: dict,
  *_args,
  **_kwargs,
) -> JSONResponse:
  """Endpoint to create a new Quote.
  """

  quote = await Quote.create(
    author=user["user_id"],
    body=data.body,
  )

  return JSONResponse(
    {
      "message": "Success.",
      "result": await quote.to_dict()
    },
    status_code=201,
  )


@use_user
@use_path_quote(path_key="quote_id")
@restrict_quote_author
async def disown_quote(
  _request: Request,
  quote: Quote,
  *_args,
  **_kwargs,
) -> JSONResponse:
  """Endpoint to disown a Quote.
  """

  quote.author = None
  await quote.save()

  return JSONResponse(
    {
      "message": "Success.",
    },
    status_code=200,
  )
