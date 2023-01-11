from http import HTTPStatus
from uuid import uuid4

import pytest
from django.shortcuts import resolve_url

from web_server.core.errors_msg import MSG_ERROR_TOKEN_USER


def test_successfull(client_api_auth, user, calculator_input):
    """
    /api/v1/users/<uuid>/calculator - POST
    """

    url = resolve_url('radiosyn:calculator', user.uuid)

    resp = client_api_auth.post(url, data=calculator_input, format='json')

    body = resp.json()

    assert resp.status_code == HTTPStatus.OK

    assert {'MBq': 6.6, 'mCi': 0.18} == body


@pytest.mark.parametrize(
    'field, value, error',
    [
        (
            'radionuclide',
            'AA-666',
            ['radionuclide: Faça uma escolha válida. AA-666 não é uma das escolhas disponíveis.'],
        ),
        ('thickness', '4 cm', ['thickness: Faça uma escolha válida. 4 cm não é uma das escolhas disponíveis.']),
        (
            'surface',
            -10,
            ['surface: Certifique-se que este valor seja maior ou igual a 0.0.'],
        ),
        ('surface', 'd-10', ['surface: Informe um número.']),
    ],
)
def test_fail_invalid(client_api_auth, user, calculator_input, field, value, error):
    """
    /api/v1/users/<uuid>/calculator - POST
    """

    calculator_input[field] = value

    url = resolve_url('radiosyn:calculator', user.uuid)

    resp = client_api_auth.post(url, data=calculator_input, format='json')

    body = resp.json()

    assert resp.status_code == HTTPStatus.OK

    assert error == body['errors']


@pytest.mark.parametrize(
    'field, error',
    [
        ('radionuclide', ['radionuclide: Este campo é obrigatório.']),
        ('thickness', ['thickness: Este campo é obrigatório.']),
        ('surface', ['surface: Este campo é obrigatório.']),
    ],
)
def test_fail_missing_fields(client_api_auth, user, calculator_input, field, error):
    """
    /api/v1/users/<uuid>/calculator - POST
    """

    calculator_input.pop(field)

    url = resolve_url('radiosyn:calculator', user.uuid)

    resp = client_api_auth.post(url, data=calculator_input, format='json')

    body = resp.json()

    assert resp.status_code == HTTPStatus.OK

    assert error == body['errors']


def test_not_allowed_method(client_api_auth, user):
    """
    /api/v1/users/<uuid>/calculator - POST
    """

    url = resolve_url('radiosyn:calculator', user.uuid)

    resp = client_api_auth.get(url, format='json')
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    resp = client_api_auth.put(url, format='json')
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    resp = client_api_auth.patch(url, format='json')
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    resp = client_api_auth.delete(url, format='json')
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED


def test_token_id_and_user_id_dont_match(client_api_auth):
    """
    /api/v1/users/<uuid>/calculator - POST
    The token does not belong to the user
    """

    url = resolve_url('radiosyn:calculator', uuid4())
    response = client_api_auth.post(url)

    assert response.status_code == HTTPStatus.UNAUTHORIZED

    body = response.json()

    assert body['errors'] == MSG_ERROR_TOKEN_USER


def test_auth(client_api, user):
    """
    /api/v1/users/<uuid>/calculator - POST
    """

    url = resolve_url('radiosyn:calculator', user.uuid)

    resp = client_api.post(url)
    assert resp.status_code == HTTPStatus.UNAUTHORIZED

    body = resp.json()

    assert body['detail'] == 'As credenciais de autenticação não foram fornecidas.'
