from http import HTTPStatus

from django.utils.translation import gettext as _
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.template.loader import render_to_string
from django.core.mail import send_mail

from web_server.core.email import DOSIMAGEM_EMAIL
from web_server.core.decorators import user_from_token_and_user_from_url
from web_server.signature.models import Signature
from web_server.signature.serializers import SignatureByUserSerializer, SignatureCreateSerizaliser
from web_server.core.errors_msg import list_errors


@api_view(['GET', 'POST'])
@user_from_token_and_user_from_url
def signature_list_create(request, user_id):

    dispatcher = {
        'GET': _signature_list,
        'POST': _signature_create,
    }

    view = dispatcher[request.method]

    return view(request, user_id)


def _signature_create(request, user_id):

    user = request.user

    serializer = SignatureCreateSerizaliser(data=request.data)

    if not serializer.is_valid():
        return Response(data={'errors': list_errors(serializer.errors)}, status=HTTPStatus.BAD_REQUEST)

    sig = serializer.save(user=user)

    serializer = SignatureByUserSerializer(instance=sig)

    context = {
        'user': user,
        'signature': serializer.data,
    }

    body_txt = render_to_string("signature/signature.txt", context)
    # body_html = render_to_string(email_template_html, context)

    send_mail('Nova assinatura', body_txt, DOSIMAGEM_EMAIL, [DOSIMAGEM_EMAIL], html_message=None)

    return Response(data=serializer.data, status=HTTPStatus.CREATED)


def _signature_list(request, user_id):

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
