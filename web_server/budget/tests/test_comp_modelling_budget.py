from http import HTTPStatus
from uuid import uuid4

import pytest
from django.core import mail
from django.shortcuts import resolve_url

from web_server.budget.views import DOSIMAGEM_EMAIL
from web_server.conftest import fake
from web_server.core.errors_msg import MSG_ERROR_TOKEN_USER

# /api/v1/users/<uuid>/budget - POST


END_POINT = 'budget:comp-modelling-budget'


@pytest.fixture
def payload():

    return {
        'service': 'Modelagem Computacional',
        'researchLine': 'Linha de pequisa 1',
        'projectDescription': fake.paragraph(nb_sentences=10),
    }


def test_send_sucessfull(client_api_auth, user, payload):

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
    assert user.profile.phone in email.body
    assert user.profile.cnpj in email.body
    assert user.profile.cpf in email.body

    assert payload['service'] in email.body
    assert payload['researchLine'] in email.body
    assert payload['projectDescription'] in email.body


@pytest.mark.parametrize(
    'field, error',
    [
        ('service', {'service': ['Este campo é obrigatório.']}),
        ('researchLine', {'researchLine': ['Este campo é obrigatório.']}),
        ('projectDescription', {'projectDescription': ['Este campo é obrigatório.']}),
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


def test_list_create_not_allowed_method(client_api_auth):

    url = resolve_url(END_POINT, uuid4())

    resp = client_api_auth.put(url)
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    resp = client_api_auth.patch(url)
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    resp = client_api_auth.delete(url)
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    resp = client_api_auth.get(url)
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED


def test_auth(client_api):

    url = resolve_url(END_POINT, uuid4())

    resp = client_api.post(url)
    body = resp.json()

    assert resp.status_code == HTTPStatus.UNAUTHORIZED

    assert 'As credenciais de autenticação não foram fornecidas.' == body['detail']


def test_user_not_have_email_verified(client_api_auth, user, payload):

    url = resolve_url(END_POINT, user.uuid)

    user.email_verified = False
    user.save()

    resp = client_api_auth.post(url, data=payload)
    body = resp.json()

    assert resp.status_code == HTTPStatus.CONFLICT

    assert 'O usuario não teve o email verificado ainda.' == body['error']


def test_token_id_and_user_id_dont_match(client_api_auth, user):

    url = resolve_url(END_POINT, uuid4())
    response = client_api_auth.post(url)

    assert response.status_code == HTTPStatus.UNAUTHORIZED

    body = response.json()

    assert MSG_ERROR_TOKEN_USER == body['errors']
