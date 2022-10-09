from http import HTTPStatus

from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.decorators import (
                                        api_view,
                                        authentication_classes,
                                        permission_classes
                                        )
from rest_framework.permissions import IsAuthenticated

from web_server.core.forms import ProfileUpdateForm

from .auth import MyTokenAuthentication
from web_server.core.errors_msg import list_errors
from web_server.api.decorators import user_from_token_and_user_from_url
from web_server.core.forms import UpdateEmailForm


User = get_user_model()


@api_view(['GET', 'PATCH'])
@authentication_classes([MyTokenAuthentication])
@permission_classes([IsAuthenticated])
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
@authentication_classes([MyTokenAuthentication])
@permission_classes([IsAuthenticated])
@user_from_token_and_user_from_url
def read_update_email(request, user_id):
    '''
    Read and update user email
    '''

    dispatcher = {
        'GET': _read_email,
        'PATCH': _update_email
    }

    view = dispatcher[request.method]

    return view(request)


def _update_email(request):

    data = request.data

    form = UpdateEmailForm(data, instance=request.user)

    if not form.is_valid():
        return Response({'errors': list_errors(form.errors)}, status=HTTPStatus.BAD_REQUEST)

    form.instance.email_verified = False
    form.save()

    return Response(status=HTTPStatus.NO_CONTENT)


def _read_email(request):
    user = request.user
    data = {'email': user.email, 'verified': user.email_verified}
    return Response(data)
