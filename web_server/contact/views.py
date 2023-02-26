import logging

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from web_server.contact.serializers import ContactSerializer
from web_server.core.email import DOSIMAGEM_EMAIL
from web_server.core.errors_msg import list_errors

logger = logging.getLogger(__name__)


class ContactView(APIView):

    permission_classes = []

    def post(self, request):

        data = request.data

        serializer = ContactSerializer(data=data)

        if not serializer.is_valid():
            return Response({'errors': list_errors(serializer.errors)}, status=status.HTTP_400_BAD_REQUEST)

        context = serializer.data

        body_txt = render_to_string('contact/contact.txt', context=context)
        body_html = render_to_string('contact/contact.html', context)

        # TODO: tratamento de erro no envio de email
        try:
            send_mail('Contato', body_txt, DOSIMAGEM_EMAIL, [DOSIMAGEM_EMAIL], html_message=body_html)
        except Exception as e:
            logger.error('Ocorreu um erro ao enviar o e-mail: %s', e)
            return Response(
                {'errors': [_('An error occurred while sending the email.')]},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)
