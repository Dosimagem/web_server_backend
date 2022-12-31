from http import HTTPStatus

import pytest
from django.core import mail
from django.shortcuts import resolve_url

from web_server.budget.views import DOSIMAGEM_EMAIL
from web_server.conftest import fake

# /api/v1/users/<uuid>/budget - POST

END_POINT = 'budget:general-budget'


@pytest.fixture
def payload():
    comments = fake.paragraph(nb_sentences=5)

    return {
        'service': 'Radiosinoviortese',
        'treatmentType': 'Tratamento do tipo 1',
        'numberOfSamples': '5',
        'frequency': '10',
        'comments': comments,
    }


def test_sucessfull(client_api_auth, user, payload):

    url = resolve_url(END_POINT, user.uuid)

    resp = client_api_auth.post(url, data=payload)

    assert resp.status_code == HTTPStatus.NO_CONTENT

    email = mail.outbox[0]

    assert 'Pedido de Orçamento' == email.subject
    assert DOSIMAGEM_EMAIL == email.from_email
    assert [DOSIMAGEM_EMAIL] == email.to

    assert user.email in email.body
    assert user.profile.name in email.body
    assert user.profile.clinic in email.body
    assert user.profile.phone_str in email.body
    assert user.profile.cnpj in email.body
    assert user.profile.cpf in email.body

    assert payload['service'] in email.body
    assert payload['treatmentType'] in email.body
    assert payload['numberOfSamples'] in email.body
    assert payload['frequency'] in email.body
    assert payload['comments'] in email.body


@pytest.mark.parametrize(
    'field, error',
    [
        ('service', {'service': ['Este campo é obrigatório.']}),
        ('treatmentType', {'treatmentType': ['Este campo é obrigatório.']}),
        ('numberOfSamples', {'numberOfSamples': ['Este campo é obrigatório.']}),
        ('frequency', {'frequency': ['Este campo é obrigatório.']}),
        ('comments', {'comments': ['Este campo é obrigatório.']}),
    ],
)
def test_missing_fields(field, error, client_api_auth, user, payload):

    payload.pop(field)

    url = resolve_url(END_POINT, user.uuid)

    resp = client_api_auth.post(url, data=payload)
    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    assert error == body['error']

    assert not len(mail.outbox)


@pytest.mark.parametrize(
    'field, value, error',
    [
        ('numberOfSamples', -1, {'numberOfSamples': ['Certifque-se de que este valor seja maior ou igual a 0.']}),
        ('frequency', -1, {'frequency': ['Certifque-se de que este valor seja maior ou igual a 0.']}),
    ],
)
def test_invalid(field, value, error, client_api_auth, user, payload):

    payload[field] = value

    url = resolve_url(END_POINT, user.uuid)

    resp = client_api_auth.post(url, data=payload)
    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    assert error == body['error']
