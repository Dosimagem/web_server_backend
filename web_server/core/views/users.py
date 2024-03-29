from http import HTTPStatus
from smtplib import SMTPException

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
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

from web_server.core.decorators import user_from_token_and_user_from_url
from web_server.core.email import send_email_verification
from web_server.core.errors_msg import list_errors
from web_server.core.forms import ProfileUpdateForm, UpdateEmailForm
from web_server.core.serializers import PhoneSerializer, VerifyEmailSerializer

User = get_user_model()


@api_view(['GET', 'PATCH'])
@user_from_token_and_user_from_url
def users_read_update(request, user_id):

    user = request.user

    if request.method == 'GET':
        return Response(data=user.to_dict())

    elif request.method == 'PATCH':
        form = ProfileUpdateForm(data=request.data, instance=user.profile)

        if not form.is_valid():
            return Response({'errors': list_errors(form.errors)}, status=HTTPStatus.BAD_REQUEST)

        form.save()

        return Response(status=HTTPStatus.NO_CONTENT)


@api_view(['PATCH', 'GET'])
@user_from_token_and_user_from_url
def read_update_email(request, user_id):
    """
    Read and update user email
    """

    dispatcher = {'GET': _read_email, 'PATCH': _update_email}

    view = dispatcher[request.method]

    return view(request)


def _update_email(request):

    data = request.data

    form = UpdateEmailForm(data, instance=request.user)

    if not form.is_valid():
        return Response({'errors': list_errors(form.errors)}, status=HTTPStatus.BAD_REQUEST)

    form.instance.email_verified = False
    form.save()

    user = form.instance

    try:
        send_email_verification(user)
    except SMTPException:
        return Response({'warning': _('Verification e-mail was not sent.')})

    return Response(status=HTTPStatus.NO_CONTENT)


def _read_email(request):
    user = request.user
    data = {'email': user.email, 'verified': user.email_verified}
    return Response(data)


@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def email_verify(request, user_id):

    serializer = VerifyEmailSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(data={'errors': list_errors(serializer.errors)}, status=HTTPStatus.BAD_REQUEST)

    token = serializer.data['token']

    try:
        user = User.objects.get(verification_email_secret=token)
    except ObjectDoesNotExist:
        return Response(
            data={'errors': [_('Invalid or expired verification token for this user.')]},
            status=HTTPStatus.BAD_REQUEST,
        )

    if not user.sent_verification_email:
        return Response(data={'errors': [_('Verification email has not yet been sent.')]}, status=HTTPStatus.CONFLICT)

    if user.email_verified:
        return Response(data={'errors': [_('Email has already been verified.')]}, status=HTTPStatus.CONFLICT)

    try:
        payload = decode(token, settings.SIGNING_KEY, algorithms=['HS256'])
    except ExpiredSignatureError:
        return Response(
            data={'errors': [_('Invalid or expired verification token for this user.')]},
            status=HTTPStatus.CONFLICT,
        )

    if not constant_time_compare(user_id, payload['id']):
        return Response(data={'errors': [_('Conflict in user id.')]}, status=HTTPStatus.CONFLICT)

    user.verification_email_secret = None
    user.email_verified = True
    user.save()

    return Response(data={'message': _('Email verified.')})


@api_view(['POST'])
@user_from_token_and_user_from_url
def email_resend(request, user_id):

    user = request.user

    try:
        send_email_verification(user)
    except SMTPException:
        return Response({'errors': [_('Verification e-mail was not sent.')]}, status=HTTPStatus.FAILED_DEPENDENCY)

    return Response(status=HTTPStatus.NO_CONTENT)


@api_view(['GET', 'PATCH'])
@user_from_token_and_user_from_url
def read_update_phone(request, user_id):

    dispatcher = {'GET': _read_phone, 'PATCH': _update_phone}

    view = dispatcher[request.method]

    return view(request)


def _read_phone(request):
    return Response(data={'phone': request.user.profile.phone_str})


def _update_phone(request):

    serializer = PhoneSerializer(data=request.data)

    if not serializer.is_valid():
        return Response({'errors': list_errors(serializer.errors)}, status=HTTPStatus.BAD_REQUEST)

    user = request.user

    user.profile.phone = serializer.validated_data['phone']
    user.save()

    return Response(status=HTTPStatus.NO_CONTENT)
