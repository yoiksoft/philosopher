"""Endpoint to disassociate yourself with a Quote.
"""

from starlette.requests import Request
from starlette.responses import JSONResponse

from app.utils.auth import requires_auth, uses_user, User
from app.services.rest.models import Quote


@requires_auth
@uses_user
async def handler(request: Request, user: User) -> JSONResponse:
  """Handler to disassociate yourself with a Quote.
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
      {"message": "You cannot disown a Quote that is not yours."},
      status_code=403,
    )

  quote.author_id = None
  await quote.save()

  return JSONResponse(
    {"message": "Success."},
    status_code=200,
  )
