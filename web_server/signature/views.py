from http import HTTPStatus

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils.translation import gettext as _

from web_server.core.decorators import user_from_token_and_user_from_url
from web_server.signature.models import Signature
from web_server.signature.serializers import SignatureByUserSerializer


@api_view(['GET'])
@user_from_token_and_user_from_url
def signature_list(request, user_id):

    user = request.user

    qs = user.signatures.all()

    serializer = SignatureByUserSerializer(qs, many=True)

    list_ = serializer.data

    return Response(data={'count': len(list_), 'row': list_})


@api_view(['GET'])
@user_from_token_and_user_from_url
def signature_read(request, user_id, signature_id):

    user = request.user

    try:
        signature = user.signatures.get(uuid=signature_id)
    except Signature.DoesNotExist:
        return Response(data={'errors': _('Subscription not found for this user')}, status=HTTPStatus.NOT_FOUND)

    serializer = SignatureByUserSerializer(signature)

    return Response(data=serializer.data)
