import pytest
from django.core import mail
from django.shortcuts import resolve_url
from rest_framework import status

from web_server.contact.views import CONTACT_EMAIL

END_POINT = resolve_url('contact:send-email')


def test_positive(client_api, contact_payload):

    resp = client_api.post(END_POINT, data=contact_payload, format='json')

    assert resp.status_code == status.HTTP_201_CREATED

    body = resp.json()
    assert body['message'] == 'Email enviado com sucesso'

    email = mail.outbox[0]

    assert email.subject == f'Contato via Site - {contact_payload["subject"]}'
    assert email.to == [CONTACT_EMAIL]
    assert email.content_subtype == 'html'

    assert contact_payload['name'] in email.body
    assert contact_payload['email'] in email.body
    assert contact_payload['role'] in email.body
    assert contact_payload['company'] in email.body
    assert contact_payload['number'] in email.body
    assert contact_payload['subject'] in email.body
    assert contact_payload['message'] in email.body


@pytest.mark.parametrize(
    'field, error',
    [
        ('name', ['name: Este campo é obrigatório.']),
        ('email', ['email: Este campo é obrigatório.']),
        ('role', ['role: Este campo é obrigatório.']),
        ('company', ['company: Este campo é obrigatório.']),
        ('number', ['number: Este campo é obrigatório.']),
        ('subject', ['subject: Este campo é obrigatório.']),
        ('message', ['message: Este campo é obrigatório.']),
    ],
)
def test_negative_missing_fields(field, error, client_api, contact_payload):

    del contact_payload[field]

    resp = client_api.post(END_POINT, data=contact_payload, format='json')

    assert resp.status_code == status.HTTP_400_BAD_REQUEST

    body = resp.json()

    assert body['errors'] == error
