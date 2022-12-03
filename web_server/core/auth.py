from dj_rest_auth.jwt_auth import JWTCookieAuthentication
from django.conf import settings


class MyJWTCookieAuthentication(JWTCookieAuthentication):
    def authenticate(self, request):
        cookie_name = getattr(settings, 'JWT_AUTH_COOKIE', None)

        if raw_access_token := request.COOKIES.get(cookie_name):

            validated_token = self.get_validated_token(raw_access_token)
            user = self.get_user(validated_token)

            return user, validated_token

        return None
