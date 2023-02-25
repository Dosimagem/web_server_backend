from http import HTTPStatus

from django.core.mail import send_mail
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import gettext as _
from rest_framework.decorators import api_view
from rest_framework.response import Response

from web_server.core.decorators import user_from_token_and_user_from_url
from web_server.core.email import DOSIMAGEM_EMAIL
from web_server.core.errors_msg import list_errors
from web_server.signature.models import Signature
from web_server.signature.serializers import (
    SignatureCreateSerizaliser,
    SignatureSerializer,
)


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

    serializer_create = SignatureCreateSerizaliser(data=request.data)

    if not serializer_create.is_valid():
        return Response(data={'errors': list_errors(serializer_create.errors)}, status=HTTPStatus.BAD_REQUEST)

    if Signature.objects.filter(user=user, plan=serializer_create.validated_data['plan']):
        return Response(
            data={'errors': [_('The user has already subscribed to this plan.')]}, status=HTTPStatus.CONFLICT
        )

    sig = serializer_create.save(user=user)

    serializer = SignatureSerializer(instance=sig)

    context = {
        'user': user,
        'signature': {**serializer.data, 'trial_time': serializer_create.validated_data['trial_time']},
    }

    body_txt = render_to_string('signature/signature.txt', context)
    body_html = render_to_string('signature/signature.html', context)

    send_mail('Nova assinatura', body_txt, DOSIMAGEM_EMAIL, [DOSIMAGEM_EMAIL], html_message=body_html)

    return Response(data=serializer.data, status=HTTPStatus.CREATED)


def _signature_list(request, user_id):

    user = request.user

    now = timezone.now()

    qs = user.signatures.filter(Q(test_period_end__gt=now) | Q(hired_period_end__gt=now))

    serializer = SignatureSerializer(qs, many=True, context={'request': request})

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

    serializer = SignatureSerializer(signature, context={'request': request})

    return Response(data=serializer.data)
