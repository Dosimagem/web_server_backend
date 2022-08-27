from http import HTTPStatus

from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token

from web_server.core.forms import SignupForm

User = get_user_model()


@api_view(['POST'])
def register(request):

    form = SignupForm(request.data)

    if not form.is_valid():
        return Response({'errors': _list_errors(form.errors)}, status=HTTPStatus.BAD_REQUEST)

    if user := form.save():
        Token.objects.create(user=user)

    data = _userToDict(user)

    return Response(data, status=HTTPStatus.CREATED)


def _userToDict(user):
    return {
        'id': user.id,
        'email': user.email,
        'token': user.auth_token.key,
        'name': user.profile.name,
        'phone': user.profile.phone,
        'institution': user.profile.institution,
        'role': user.profile.role,
    }


def _list_errors(errors):

    list_ = []

    for field_name, field_errors in errors.items():
        for error in field_errors:
            if error == 'This field is required.':
                msg = field_name.capitalize() + ' field is required.'
                list_.append(msg)
            else:
                list_.append(error)

    return list_
