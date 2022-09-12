from http import HTTPStatus

from django.db import transaction
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from djangorestframework_camel_case.render import CamelCaseJSONRenderer


from web_server.core.forms import MyUserCreationForm, ProfileCreateForm
from .errors_msg import list_errors

User = get_user_model()


class ProfileValidataionError(Exception):
    def __init__(self, form_error, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_error = form_error


def _register_user_profile_token(form_user, data):
    with transaction.atomic():

        user = form_user.save()

        data['user'] = user

        form_profile = ProfileCreateForm(data, instance=user.profile)

        if not form_profile.is_valid():
            raise ProfileValidataionError(form_error=form_profile.errors)

        form_profile.save()
        Token.objects.create(user=user)

        data = {'id': user.uuid, 'token': user.auth_token.key, 'is_staff': user.is_staff}

        return Response(data, status=HTTPStatus.CREATED)


@api_view(['POST'])
def register(request):

    data = request.data

    form_user = MyUserCreationForm(data)

    if not form_user.is_valid():
        return Response({'errors': list_errors(form_user.errors)}, status=HTTPStatus.BAD_REQUEST)

    try:
        return _register_user_profile_token(form_user, data)

    except ProfileValidataionError as e:
        return Response({'errors': list_errors(e.form_error)}, status=HTTPStatus.BAD_REQUEST)


class MyObtainAuthToken(ObtainAuthToken):
    '''
    Error response example
    {
    "errors": ["Username field is required.", "Password field is required."]
    }
    '''
    renderer_classes = (CamelCaseJSONRenderer, )

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid(raise_exception=False):
            return Response({'errors': list_errors(serializer.errors)}, status=HTTPStatus.BAD_REQUEST)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'id': user.uuid, 'token': token.key, 'is_staff': user.is_staff})
