from http import HTTPStatus
from smtplib import SMTPException

from dj_rest_auth.jwt_auth import set_jwt_cookies
from dj_rest_auth.utils import jwt_encode
from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.response import Response

from web_server.core.email import send_email_verification
from web_server.core.errors_msg import list_errors
from web_server.core.forms import MyUserCreationForm, ProfileCreateForm

User = get_user_model()


class ProfileValidationError(Exception):
    def __init__(self, form_error, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_error = form_error


def _register_user_profile_token(form_user, data):
    with transaction.atomic():

        user = form_user.save()

        data['user'] = user

        form_profile = ProfileCreateForm(data, instance=user.profile)

        if not form_profile.is_valid():
            raise ProfileValidationError(form_error=form_profile.errors)

        form_profile.save()

        data = {'id': user.uuid, 'is_staff': user.is_staff}

        return Response(data, status=HTTPStatus.CREATED)


@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def register(request):

    data = request.data

    # TODO: put here form for clean the mask of cpf and cnpj

    form_user = MyUserCreationForm(data)

    if not form_user.is_valid():
        return Response({'errors': list_errors(form_user.errors)}, status=HTTPStatus.BAD_REQUEST)

    try:
        response = _register_user_profile_token(form_user, data)

    except ProfileValidationError as e:
        return Response({'errors': list_errors(e.form_error)}, status=HTTPStatus.BAD_REQUEST)

    # TODO: needs treatment if email fails

    user = form_user.instance

    try:
        send_email_verification(user)
    except SMTPException:
        response.data['warning'] = 'Email de verificação não foi enviado.'

    access_token, refresh_token = jwt_encode(user)
    set_jwt_cookies(response, access_token, refresh_token)

    return response
