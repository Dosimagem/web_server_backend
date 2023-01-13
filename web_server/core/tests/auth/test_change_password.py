from http import HTTPStatus

import pytest
from django.shortcuts import resolve_url

from web_server.core.errors_msg import MSG_ERROR_TOKEN_USER

END_POINT = 'core:change-password'


@pytest.fixture
def payload(register_infos):
    password = register_infos['password1']
    return {'old_password': password, 'new_password1': '123455!!', 'new_password2': '123455!!'}


def test_change_password(client_api_auth, user, payload):

    url = resolve_url(END_POINT, user_id=user.uuid)

    resp = client_api_auth.post(url, data=payload, formt='json')

    assert HTTPStatus.OK == resp.status_code

    body = resp.json()

    user.refresh_from_db()

    assert user.check_password('123455!!')

    assert body['message'] == 'Senha atualizada.'


def test_passwords_dont_mach(client_api_auth, user, payload):

    payload['new_password2'] = payload['new_password2'] + '12'

    url = resolve_url(END_POINT, user_id=user.uuid)

    resp = client_api_auth.post(url, data=payload, formt='json')

    assert HTTPStatus.BAD_REQUEST == resp.status_code

    body = resp.json()

    assert body['errors'] == ['new_password2: Os dois campos de senha não correspondem.']


@pytest.mark.parametrize(
    'field, error',
    [
        ('old_password', ['old_password: Este campo é obrigatório.']),
        ('new_password1', ['new_password1: Este campo é obrigatório.']),
        ('new_password2', ['new_password2: Este campo é obrigatório.']),
    ],
)
def test_missing_fields(client_api_auth, field, error, user, payload):

    payload.pop(field)

    url = resolve_url(END_POINT, user_id=user.uuid)

    resp = client_api_auth.post(url, data=payload, formt='json')

    assert HTTPStatus.BAD_REQUEST == resp.status_code

    body = resp.json()

    assert body['errors'] == error


def test_wrong_old_password(client_api_auth, user, payload):

    payload['old_password'] = payload['old_password'] + '11'

    url = resolve_url(END_POINT, user_id=user.uuid)

    resp = client_api_auth.post(url, data=payload, formt='json')

    assert HTTPStatus.BAD_REQUEST == resp.status_code

    body = resp.json()

    assert body['errors'] == ['old_password: Password antigo não está correto.']


def test_token_id_and_user_id_dont_match(client_api_auth, second_user):
    """
    The token does not belong to the user
    """

    url = resolve_url(END_POINT, user_id=second_user.uuid)
    response = client_api_auth.post(url)

    assert response.status_code == HTTPStatus.UNAUTHORIZED

    body = response.json()

    assert body['errors'] == MSG_ERROR_TOKEN_USER


def test_not_allowed_method(client_api_auth, user):

    url = resolve_url(END_POINT, user.uuid)

    resp = client_api_auth.get(url)
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    resp = client_api_auth.put(url)
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    resp = client_api_auth.patch(url)
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    resp = client_api_auth.delete(url)
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED


def test_auth(client_api, user):

    url = resolve_url(END_POINT, user_id=user.uuid)

    resp = client_api.post(url)

    assert resp.status_code == HTTPStatus.UNAUTHORIZED

    body = resp.json()

    assert body['detail'] == 'As credenciais de autenticação não foram fornecidas.'
