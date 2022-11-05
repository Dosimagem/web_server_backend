from http import HTTPStatus
from uuid import uuid4

import pytest
from django.core import mail
from django.shortcuts import resolve_url


from web_server.conftest import fake
from web_server.budget.views import DOSIMAGEM_EMAIL

# /api/v1/users/<uuid>/budget - POST


@pytest.fixture
def payload():
    comments = fake.paragraph(nb_sentences=5)

    return {
        'service': 'Dosimetria',
        'treatment_type': 'Tratamento do tipo 1',
        'number_of_samples': '5',
        'frequency': '10',
        'comments': comments,
    }


def test_send_sucessfull(client_api_auth, user, payload):

    url = resolve_url('budget:send_email', user.uuid)

    resp = client_api_auth.post(url, data=payload)

    assert resp.status_code == HTTPStatus.NO_CONTENT

    email = mail.outbox[0]

    assert 'Pedido de Orçamento' == email.subject
    assert DOSIMAGEM_EMAIL == email.from_email
    assert [DOSIMAGEM_EMAIL] == email.to

    assert user.email in email.body
    assert user.profile.name in email.body
    assert user.profile.clinic in email.body
    assert user.profile.phone in email.body
    assert user.profile.cnpj in email.body
    assert user.profile.cpf in email.body

    assert payload['service'] in email.body
    assert payload['treatment_type'] in email.body
    assert payload['number_of_samples'] in email.body
    assert payload['frequency'] in email.body
    assert payload['comments'] in email.body


@pytest.mark.parametrize(
    'field, error',
    [
        ('service', {'service': ['Este campo é obrigatório.']}),
        ('treatment_type', {'treatmentType': ['Este campo é obrigatório.']}),
        ('number_of_samples', {'numberOfSamples': ['Este campo é obrigatório.']}),
        ('frequency', {'frequency': ['Este campo é obrigatório.']}),
        ('comments', {'comments': ['Este campo é obrigatório.']}),
    ],
)
def test_missing_fields(field, error, client_api_auth, user, payload):

    payload.pop(field)

    url = resolve_url('budget:send_email', user.uuid)

    resp = client_api_auth.post(url, data=payload)
    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    assert error == body['error']

    assert not len(mail.outbox)


def test_list_create_not_allowed_method(client_api_auth):

    url = resolve_url('budget:send_email', uuid4())

    resp = client_api_auth.put(url)
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    resp = client_api_auth.patch(url)
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    resp = client_api_auth.delete(url)
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    resp = client_api_auth.get(url)
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED


def test_auth(client_api):

    url = resolve_url('budget:send_email', uuid4())

    resp = client_api.post(url)
    body = resp.json()

    assert resp.status_code == HTTPStatus.UNAUTHORIZED

    assert 'As credenciais de autenticação não foram fornecidas.' == body['detail']


def test_user_not_have_email_verified(client_api_auth, user, payload):

    url = resolve_url('budget:send_email', user.uuid)

    user.email_verified = False
    user.save()

    resp = client_api_auth.post(url, data=payload)
    body = resp.json()

    assert resp.status_code == HTTPStatus.CONFLICT

    assert 'O usuario não teve o email verificado ainda.' == body['error']


@pytest.mark.parametrize(
    'field, value, error',
    [
        ('number_of_samples', -1, {'numberOfSamples': ['Certifque-se de que este valor seja maior ou igual a 0.']}),
        ('frequency', -1, {'frequency': ['Certifque-se de que este valor seja maior ou igual a 0.']}),
    ],
)
def test_invalid(field, value, error, client_api_auth, user, payload):

    payload[field] = value

    url = resolve_url('budget:send_email', user.uuid)

    resp = client_api_auth.post(url, data=payload)
    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    assert error == body['error']
