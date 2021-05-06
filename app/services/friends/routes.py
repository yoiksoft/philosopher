from starlette.routing import Route

from app.services.friends import endpoints


ROUTES = [
  Route(
    "/{user_id}/friends",
    endpoint=endpoints.get_friends,
    methods=["GET"]),
  Route(
    "/{user_id}/friends",
    endpoint=endpoints.accept_request,
    methods=["POST"]),
  Route(
    "/{user_id}/friends/{friend_id}",
    endpoint=endpoints.remove_friend,
    methods=["DELETE"]),
  Route(
    "/{user_id}/requests",
    endpoint=endpoints.get_requests,
    methods=["GET"]),
  Route(
    "/{user_id}/requests/{request_id}",
    endpoint=endpoints.create_request,
    methods=["PUT"]),
  Route(
    "/{user_id}/requests/{request_id}",
    endpoint=endpoints.delete_request,
    methods=["DELETE"]),
]
