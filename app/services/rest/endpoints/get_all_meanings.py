"""Endpoint to get all Meanings for a Quote.
"""

from starlette.requests import Request
from starlette.responses import JSONResponse

from app.utils.auth import requires_auth, uses_user, User
from app.services.rest.models import Quote, Meaning


@requires_auth
@uses_user
async def handler(request: Request, user: User) -> JSONResponse:
  """Handler to get all Meanings for a Quote.
  """

  quote_id = request.path_params["quote_id"]
  quote: Quote = await Quote.filter(id=quote_id).first()

  if not quote:
    return JSONResponse(
      {"message": "Quote does not exist."},
      status_code=404,
    )

  if quote.author_id != user.user_id:
    return JSONResponse(
      {
        "message":
          "Only the author is permitted to see Meanings for this Quote."
      },
      status_code=403)

  meanings = await Meaning.filter(quote=quote)

  return JSONResponse(
    {
      "message": "Success.",
      "data": [meaning.to_dict() for meaning in meanings]
    },
    status_code=200,
  )
