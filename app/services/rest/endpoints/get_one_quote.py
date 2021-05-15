"""Endpoint to get a specific Quote.
"""

from starlette.requests import Request
from starlette.responses import JSONResponse

from app.utils.auth import requires_auth
from app.services.rest.models import Quote


@requires_auth
async def handler(request: Request) -> JSONResponse:
  """Handler to get a specific Quote.
  """

  quote_id = request.path_params["quote_id"]
  quote = await Quote.filter(id=quote_id).first()

  if not quote:
    return JSONResponse({"message": "Not found."}, status_code=404)

  return JSONResponse({
    "message": "Success.",
    "data": quote.to_dict()
  },
                      status_code=200)
