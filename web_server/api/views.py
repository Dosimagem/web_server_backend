from http import HTTPStatus

from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.decorators import (
                                        api_view,
                                        authentication_classes,
                                        permission_classes
                                        )
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken

from web_server.core.forms import SignupForm

User = get_user_model()


class MyTokenAuthentication(TokenAuthentication):
    keyword = 'Bearer'


@api_view(['POST'])
def register(request):

    form = SignupForm(request.data)

    if not form.is_valid():
        return Response({'errors': _list_errors(form.errors)}, status=HTTPStatus.BAD_REQUEST)

    if user := form.save():
        Token.objects.create(user=user)

    data = {'id': user.uuid, 'token': user.auth_token.key, 'is_staff': user.is_staff}

    return Response(data, status=HTTPStatus.CREATED)


class MyObtainAuthToken(ObtainAuthToken):
    '''
    Error response example
    {
    "errors": ["Username field is required.", "Password field is required."]
    }
    '''
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid(raise_exception=False):
            return Response({'errors': _list_errors(serializer.errors)}, status=HTTPStatus.BAD_REQUEST)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'id': user.uuid, 'token': token.key, 'is_staff': user.is_staff})


@api_view(['GET'])
@authentication_classes([MyTokenAuthentication])
@permission_classes([IsAuthenticated])
def users(request, id):

    if user := User.objects.filter(uuid=id).first():
        return Response(data=_user_to_dict(user))

    return Response({}, status=HTTPStatus.NOT_FOUND)


def _user_to_dict(user):
    return dict(
        name=user.profile.name,
        phone=user.profile.phone,
        role=user.profile.role,
        institution=user.profile.institution,
        email=user.email
    )


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
