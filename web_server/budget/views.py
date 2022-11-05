from http import HTTPStatus

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from rest_framework.decorators import api_view
from rest_framework.response import Response

from web_server.budget.serializers import BudgetSerilizer

DOSIMAGEM_EMAIL = settings.DEFAULT_FROM_EMAIL


@api_view(['POST'])
def send_email(request, user_id):

    user = request.user

    if user.email_not_verified():
        return Response(data={'error': 'O usuario não teve o email verificado ainda.'}, status=HTTPStatus.CONFLICT)

    serializer = BudgetSerilizer(data=request.data)

    if not serializer.is_valid():
        return Response(data={'error': serializer.errors}, status=HTTPStatus.BAD_REQUEST)

    context = serializer.data
    context['user'] = user

    body = render_to_string('budget/email.txt', context)

    send_mail('Pedido de Orçamento', body, DOSIMAGEM_EMAIL, [DOSIMAGEM_EMAIL])

    return Response(status=HTTPStatus.NO_CONTENT)
