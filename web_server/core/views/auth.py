from http import HTTPStatus


from dj_rest_auth.jwt_auth import set_jwt_cookies
from dj_rest_auth.views import LoginView
from rest_framework.response import Response

from web_server.core.errors_msg import list_errors


class MyLoginView(LoginView):
    def post(self, request, *args, **kwargs):
        self.request = request
        self.serializer = self.get_serializer(data=self.request.data)
        if not self.serializer.is_valid():
            return Response({'errors': list_errors(self.serializer.errors)}, status=HTTPStatus.BAD_REQUEST)

        self.login()
        return self.get_response()

    def get_response(self):

        data = {'id': self.user.uuid, 'is_staff': self.user.is_staff}

        response = Response(data, status=HTTPStatus.OK)
        set_jwt_cookies(response, self.access_token, self.refresh_token)
        return response


# TODO: logout
# TODO: Refesh token
