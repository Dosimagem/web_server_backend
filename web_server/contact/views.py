import logging

from django.core.mail import EmailMessage
from django.utils.translation import gettext as _
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from web_server.contact.serializers import ContactSerializer
from web_server.core.errors_msg import list_errors

logger = logging.getLogger(__name__)

CONTACT_EMAIL = 'contact@dosimagem.com'


def _build_html_body(data):
    return (
        '<p>Olá você acaba de receber uma mensagem através da página de contato do site da Dosimagem,</p>'
        '<p>Segue abaixo a mensagem enviada por {name}:</p>'
        '<p style="padding-top: 12px; padding-right: 12px; padding-bottom: 12px; border-left: 4px solid rgb(208, 208, 208); font-style: italic;">'
        '<strong>&nbsp; &nbsp;{subject}</strong></p>'
        '<p style="padding: 12px; border-left: 4px solid #d0d0d0; font-style: italic;">'
        '<strong>{message}</strong></p>'
        '<p>Tomar as providências cabíveis.</p>'
        '<p>&nbsp;</p>'
        '<p style="text-align: left;"><strong>Dados do contato</strong></p>'
        '<table style="border-collapse: collapse; width: 43.3628%; border-width: 1px; border-style: solid; height: 105px;" border="1">'
        '<colgroup><col style="width: 13.1558%;"><col style="width: 86.8442%;"></colgroup>'
        '<tbody>'
        '<tr style="height: 21px;"><td>Nome</td><td>{name}</td></tr>'
        '<tr style="height: 21px;"><td>E-mail</td><td>{email}</td></tr>'
        '<tr style="height: 21px;"><td>Cargo</td><td>{role}</td></tr>'
        '<tr style="height: 21px;"><td>Clínica</td><td>{company}</td></tr>'
        '<tr style="height: 21px;"><td>Telefone</td><td>{number}</td></tr>'
        '</tbody>'
        '</table>'
    ).format(**data)


class ContactView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        data = request.data

        serializer = ContactSerializer(data=data)

        if not serializer.is_valid():
            return Response({'errors': list_errors(serializer.errors)}, status=status.HTTP_400_BAD_REQUEST)

        validated = serializer.validated_data

        subject = f'Contato via Site - {validated["subject"]}'
        body_html = _build_html_body(validated)

        try:
            email = EmailMessage(
                subject=subject,
                body=body_html,
                to=[CONTACT_EMAIL],
            )
            email.content_subtype = 'html'
            email.send()
        except Exception as e:
            logger.error('Ocorreu um erro ao enviar o e-mail: %s', e)
            return Response(
                {'errors': [{'detail': _('An error occurred while sending the email.')}]},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response({'message': 'Email enviado com sucesso'}, status=status.HTTP_201_CREATED)
