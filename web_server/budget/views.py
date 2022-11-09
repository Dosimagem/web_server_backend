from http import HTTPStatus

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from rest_framework.decorators import api_view
from rest_framework.response import Response

from web_server.budget.serializers import (
    CompModelBudgetSerilizer,
    GeneralBudgetSerilizer,
)
from web_server.core.decorators import user_from_token_and_user_from_url

DOSIMAGEM_EMAIL = settings.DEFAULT_FROM_EMAIL


@api_view(['POST'])
@user_from_token_and_user_from_url
def general_budget_mail(request, user_id):

    user = request.user

    if user.email_not_verified():
        return Response(data={'error': 'O usuario não teve o email verificado ainda.'}, status=HTTPStatus.CONFLICT)

    serializer = GeneralBudgetSerilizer(data=request.data)

    if not serializer.is_valid():
        return Response(data={'error': serializer.errors}, status=HTTPStatus.BAD_REQUEST)

    context = serializer.data
    context['user'] = user

    body = render_to_string('budget/general_budget.txt', context)

    send_mail('Pedido de Orçamento', body, DOSIMAGEM_EMAIL, [DOSIMAGEM_EMAIL])

    return Response(status=HTTPStatus.NO_CONTENT)


@api_view(['POST'])
@user_from_token_and_user_from_url
def comp_model_budget_mail(request, user_id):
    user = request.user

    if user.email_not_verified():
        return Response(data={'error': 'O usuario não teve o email verificado ainda.'}, status=HTTPStatus.CONFLICT)

    serializer = CompModelBudgetSerilizer(data=request.data)

    if not serializer.is_valid():
        return Response(data={'error': serializer.errors}, status=HTTPStatus.BAD_REQUEST)

    context = serializer.data
    context['user'] = user

    body = render_to_string('budget/comp_model_budget.txt', context)

    send_mail('Pedido de Orçamento', body, DOSIMAGEM_EMAIL, [DOSIMAGEM_EMAIL])

    return Response(status=HTTPStatus.NO_CONTENT)