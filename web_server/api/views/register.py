from http import HTTPStatus

from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from djangorestframework_camel_case.render import CamelCaseJSONRenderer

from web_server.core.forms import SignupForm
from .utils import list_errors

User = get_user_model()


@api_view(['POST'])
def register(request):

    form = SignupForm(request.data)

    if not form.is_valid():
        return Response({'errors': list_errors(form.errors)}, status=HTTPStatus.BAD_REQUEST)

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
    renderer_classes = (CamelCaseJSONRenderer, )

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid(raise_exception=False):
            return Response({'errors': list_errors(serializer.errors)}, status=HTTPStatus.BAD_REQUEST)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'id': user.uuid, 'token': token.key, 'is_staff': user.is_staff})
