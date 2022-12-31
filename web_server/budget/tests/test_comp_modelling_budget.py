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
    assert user.profile.phone_str in email.body
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
