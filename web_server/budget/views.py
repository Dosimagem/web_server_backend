from http import HTTPStatus

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from rest_framework.decorators import api_view
from rest_framework.response import Response

from web_server.budget.serializers import GeneralBudgetSerializer
from web_server.core.decorators import user_from_token_and_user_from_url
from web_server.core.errors_msg import list_errors

from .budget_svc import BudgetChoice

DOSIMAGEM_EMAIL = settings.DEFAULT_FROM_EMAIL


@api_view(['POST'])
@user_from_token_and_user_from_url
def general_budget_mail(request, user_id):

    user = request.user

    if user.email_not_verified():
        return Response(
            data={'errors': [_('The user does not have a verified email yet.')]}, status=HTTPStatus.CONFLICT
        )

    serializer = GeneralBudgetSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(data={'errors': list_errors(serializer.errors)}, status=HTTPStatus.BAD_REQUEST)

    service = serializer.data['service']

    budget = BudgetChoice(service_name=service)
    serializerClass = budget.get_serializer()
    email_template_txt, email_template_html = budget.get_email_template()
    serializer = serializerClass(data=request.data)

    if not serializer.is_valid():
        return Response(data={'errors': list_errors(serializer.errors)}, status=HTTPStatus.BAD_REQUEST)

    context = serializer.data
    context['service'] = service
    context['user'] = user

    body_txt = render_to_string(email_template_txt, context)
    body_html = render_to_string(email_template_html, context)

    send_mail('Pedido de Orçamento', body_txt, DOSIMAGEM_EMAIL, [DOSIMAGEM_EMAIL], html_message=body_html)

    return Response(status=HTTPStatus.NO_CONTENT)
