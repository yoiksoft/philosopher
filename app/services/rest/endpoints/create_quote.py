"""Endpoint to create a new Quote.
"""

from starlette.requests import Request
from starlette.responses import JSONResponse
from tortoise.exceptions import ValidationError

from app.utils.auth import requires_auth, uses_user, User
from app.services.rest.models import Quote


@requires_auth
@uses_user
async def handler(request: Request, user: User) -> JSONResponse:
  """Handler to create a new Quote.
  """

  try:
    request_body = await request.json()
  except:
    return JSONResponse(
      {"message": "Missing request body."},
      status_code=400,
    )

  try:
    body = request_body["body"]
  except KeyError:
    return JSONResponse(
      {"message": "Missing body field in request body."},
      status_code=400,
    )

  try:
    quote = await Quote.create(body=body, author_id=user.user_id)
  except ValidationError as exception:
    return JSONResponse(
      {
        "message": "Invalid body failed validation.",
        "data": str(exception)
      },
      status_code=400,
    )

  return JSONResponse(
    {
      "message": "Success.",
      "data": quote.to_dict()
    },
    status_code=201,
  )
