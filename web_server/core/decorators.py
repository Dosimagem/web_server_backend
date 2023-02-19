from functools import wraps
from http import HTTPStatus

from rest_framework.response import Response

from web_server.core.errors_msg import MSG_ERROR_TOKEN_USER


def user_from_token_and_user_from_url(view):
    @wraps(view)
    def decorator(request, *args, **kwargs):
        user_from_token = request.user.uuid
        user_from_url = kwargs['user_id']
        if user_from_token != user_from_url:
            return Response({'errors': MSG_ERROR_TOKEN_USER}, status=HTTPStatus.UNAUTHORIZED,)

        return view(request, *args, **kwargs)

    return decorator
