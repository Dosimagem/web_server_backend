from http import HTTPStatus

from dj_rest_auth.jwt_auth import (
    CookieTokenRefreshSerializer,
    set_jwt_access_cookie,
    set_jwt_cookies,
    set_jwt_refresh_cookie,
    unset_jwt_cookies,
)
from dj_rest_auth.views import LoginView, LogoutView
from django.conf import settings
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.settings import api_settings as jwt_settings
from rest_framework_simplejwt.views import TokenRefreshView

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


class MyLogoutView(LogoutView):
    def logout(self, request):

        response = Response({'detail': 'Logout.'}, status=HTTPStatus.OK)
        unset_jwt_cookies(response)

        return response


class MyRefreshViewWithCookieSupport(TokenRefreshView):
    serializer_class = CookieTokenRefreshSerializer

    def finalize_response(self, request, response, *args, **kwargs):
        if response.status_code == HTTPStatus.OK and 'access' in response.data:
            set_jwt_access_cookie(response, response.data['access'])
            if not settings.JWT_AUTH_IN_BODY:
                response.data.pop('access')
            response.data['access_token_expiration'] = timezone.now() + jwt_settings.ACCESS_TOKEN_LIFETIME
        if response.status_code == HTTPStatus.OK and 'refresh' in response.data:
            set_jwt_refresh_cookie(response, response.data['refresh'])
            if not settings.JWT_AUTH_IN_BODY:
                response.data.pop('refresh')
            response.data['refrash_token_expiration'] = timezone.now() + jwt_settings.REFRESH_TOKEN_LIFETIME

        return super().finalize_response(request, response, *args, **kwargs)


@api_view(['GET'])
def am_i_auth(request):
    return Response({'message': f'{request.user.profile.name} is authenticated.'})
