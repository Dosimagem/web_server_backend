from http import HTTPStatus

from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed, TokenError
from rest_framework_simplejwt.settings import api_settings


class InvalidToken(AuthenticationFailed):
    status_code = HTTPStatus.UNAUTHORIZED
    default_detail = _('Token is invalid or expired')
    default_code = 'token_not_valid'


class MyJWTAuthentication(JWTAuthentication):
    def get_validated_token(self, raw_token):
        """
        Validates an encoded JSON web token and returns a validated token
        wrapper object.
        """
        messages = []
        for AuthToken in api_settings.AUTH_TOKEN_CLASSES:
            try:
                return AuthToken(raw_token)
            except TokenError as e:
                messages.append(
                    {
                        'token_class': AuthToken.__name__,
                        'token_type': AuthToken.token_type,
                        'message': e.args[0],
                    }
                )

        raise InvalidToken(
            {
                'detail': _('Given token not valid for any token type'),
                'messages': messages,
            }
        )


class MyJWTCookieAuthentication(MyJWTAuthentication):
    def authenticate(self, request):
        cookie_name = getattr(settings, 'JWT_AUTH_COOKIE', None)

        if raw_access_token := request.COOKIES.get(cookie_name):

            validated_token = self.get_validated_token(raw_access_token)
            user = self.get_user(validated_token)

            return user, validated_token

        return None
