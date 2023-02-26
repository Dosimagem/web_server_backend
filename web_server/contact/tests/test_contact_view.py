import pytest
from django.core import mail
from django.shortcuts import resolve_url
from rest_framework import status

from web_server.core.email import DOSIMAGEM_EMAIL

END_POINT = resolve_url('contact:send-email')


def test_positive(client_api, contact_payload):

    resp = client_api.post(END_POINT, data=contact_payload, format='json')

    assert resp.status_code == status.HTTP_204_NO_CONTENT

    email = mail.outbox[0]

    assert 'Contato' == email.subject
    assert DOSIMAGEM_EMAIL == email.from_email

    assert contact_payload['fullName'] in email.body
    assert contact_payload['email'] in email.body
    assert contact_payload['role'] in email.body
    assert contact_payload['clinic'] in email.body
    assert contact_payload['phone'] in email.body
    assert contact_payload['subject'] in email.body
    assert contact_payload['message'] in email.body


@pytest.mark.parametrize(
    'field, error',
    [
        ('fullName', ['full_name: Este campo é obrigatório.']),
        ('email', ['email: Este campo é obrigatório.']),
        ('role', ['role: Este campo é obrigatório.']),
        ('clinic', ['clinic: Este campo é obrigatório.']),
        ('phone', ['phone: Este campo é obrigatório.']),
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
