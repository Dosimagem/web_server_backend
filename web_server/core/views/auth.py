from http import HTTPStatus
from smtplib import SMTPException

from dj_rest_auth.jwt_auth import (
    CookieTokenRefreshSerializer,
    set_jwt_access_cookie,
    set_jwt_cookies,
    set_jwt_refresh_cookie,
    unset_jwt_cookies,
)
from dj_rest_auth.views import LoginView, LogoutView
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.utils.crypto import constant_time_compare
from django.utils.translation import gettext as _
from jwt import decode
from jwt.exceptions import ExpiredSignatureError
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.settings import api_settings as jwt_settings
from rest_framework_simplejwt.views import TokenRefreshView

from web_server.core.decorators import user_from_token_and_user_from_url
from web_server.core.email import send_reset_password
from web_server.core.errors_msg import list_errors
from web_server.core.serializers import (
    ChangePasswordSerializer,
    ResetPasswordConfirmSerializer,
    ResetPasswordSerializer,
)

User = get_user_model()


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

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        return Response(serializer.validated_data, status=HTTPStatus.OK)


@api_view(['GET'])
def am_i_auth(request):
    return Response({'message': f'{request.user.profile.name} is authenticated.'})


@api_view(['POST'])
@user_from_token_and_user_from_url
def change_password(request, user_id):

    user = request.user
    data = request.data

    serializer = ChangePasswordSerializer(data=data, instance=user)

    if not serializer.is_valid():
        return Response(data={'errors': list_errors(serializer.errors)}, status=HTTPStatus.BAD_REQUEST)

    password = serializer.validated_data['new_password1']
    user.set_password(password)
    user.save()

    return Response(data={'message': _('Updated password.')})


@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def reset_password(request):

    serializer = ResetPasswordSerializer(data=request.data)

    if not serializer.is_valid():
        return Response({'errors': list_errors(serializer.errors)}, status=HTTPStatus.BAD_REQUEST)

    try:
        user = User.objects.get(email=serializer.validated_data['email'])
    except ObjectDoesNotExist:
        return Response({'errors': [_('This e-mail is not registered.')]}, status=HTTPStatus.BAD_REQUEST)

    try:
        send_reset_password(user)
    except SMTPException:
        return Response({'errors': [_('E-mail not sent.')]}, status=HTTPStatus.FAILED_DEPENDENCY)

    return Response({'message': _('E-mail sent.')})


@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def reset_password_confirm(request, user_id):

    serializer = ResetPasswordConfirmSerializer(data=request.data)

    if not serializer.is_valid():
        return Response({'errors': list_errors(serializer.errors)}, status=HTTPStatus.BAD_REQUEST)

    new_password = serializer.validated_data['new_password1']
    token = serializer.validated_data['token']

    try:
        user = User.objects.get(uuid=user_id, reset_password_secret=token)
    except ObjectDoesNotExist:
        return Response(
            data={'errors': [_('Invalid or expired verification token for this user.')]},
            status=HTTPStatus.BAD_REQUEST,
        )

    if not user.sent_reset_password_email:
        return Response(data={'errors': [_('Verification e-mail was not sent.')]}, status=HTTPStatus.CONFLICT)

    try:
        payload = decode(token, settings.SIGNING_KEY, algorithms=['HS256'])
    except ExpiredSignatureError:
        return Response(
            data={'errors': [_('Invalid or expired verification token for this user.')]},
            status=HTTPStatus.CONFLICT,
        )

    if not constant_time_compare(user_id, payload['id']):
        return Response(data={'errors': [_('Conflict in user id.')]}, status=HTTPStatus.CONFLICT)

    user.set_password(new_password)
    user.reset_password_secret = None
    user.sent_reset_password_email = False
    user.save()

    return Response(status=HTTPStatus.NO_CONTENT)
