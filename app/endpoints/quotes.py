"""Quote related endpoints.
"""

from starlette.requests import Request
from starlette.responses import JSONResponse

from app.utils.decorators import (
  validate_body,
  use_path_model,
  use_user,
  restrict,
)
from app.utils.restrictions import author_of_quote
from app.schemas import QuoteSchema
from app.models import Author, Quote


@use_path_model(Quote, path_key="quote_id")
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
@validate_body(QuoteSchema)
@use_user
async def create_quote(
  _request: Request,
  user: Author,
  data: dict,
  *_args,
  **_kwargs,
) -> JSONResponse:
  """Endpoint to create a new Quote.
  """

  quote = await Quote.create(
    author=user.user_id,
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
@use_path_model(Quote, path_key="quote_id")
@restrict(author_of_quote, assertion=True)
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
