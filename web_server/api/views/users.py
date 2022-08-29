from http import HTTPStatus

from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.decorators import (
                                        api_view,
                                        authentication_classes,
                                        permission_classes
                                        )
from rest_framework.permissions import IsAuthenticated

from .utils import user_to_dict, MyTokenAuthentication

User = get_user_model()


@api_view(['GET'])
@authentication_classes([MyTokenAuthentication])
@permission_classes([IsAuthenticated])
def users(request, id):

    if user := User.objects.filter(uuid=id).first():
        return Response(data=user_to_dict(user))

    return Response({}, status=HTTPStatus.NOT_FOUND)
