from http import HTTPStatus
from uuid import uuid4

from django.shortcuts import resolve_url

from web_server.api.views.errors_msg import MSG_ERROR_TOKEN_USER


def test_update(client_api_auth, user):
    '''
    /api/v1/users/<uuid>/email - PATCH
    '''

    new_email = 'user1_new@email.com'

    url = resolve_url('api:update-email', user.uuid)

    resp = client_api_auth.patch(url, data={'email': new_email}, format='json')
    assert resp.status_code == HTTPStatus.NO_CONTENT

    user.refresh_from_db()

    assert user.email == new_email

    assert not user.email_verify


def test_not_allowed_method(client_api_auth, user):

    url = resolve_url('api:update-email', user.uuid)

    resp = client_api_auth.get(url)
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    resp = client_api_auth.post(url)
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    resp = client_api_auth.put(url)
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    resp = client_api_auth.delete(url)
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED


def test_allowed_url(client_api_auth, user):

    url = resolve_url('api:update-email', user.uuid)

    resp = client_api_auth.options(url)

    assert resp.status_code == HTTPStatus.OK

    options = resp.headers['Allow'].split(',')

    for o in options:
        assert o.strip() in ['OPTIONS', 'PATCH']


def test_update_email_token_id_and_user_id_dont_match(client_api_auth, user):
    '''
    /api/v1/users/<uuid>/calibrations/ - PATCH
    '''

    url = resolve_url('api:update-email', uuid4())
    response = client_api_auth.patch(url)

    assert response.status_code == HTTPStatus.UNAUTHORIZED

    body = response.json()

    assert body['errors'] == MSG_ERROR_TOKEN_USER


def test_fail_update_invalid_email(client_api_auth, user):
    '''
    /api/v1/users/<uuid>/email - PATCH
    '''

    new_email = 'user1_newemail.com'

    url = resolve_url('api:update-email', user.uuid)

    resp = client_api_auth.patch(url, data={'email': new_email}, format='json')
    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert body['errors'] == ['Insira um endereço de email válido.']


def test_fail_update_email_must_be_unique(client_api_auth, user, second_user):
    '''
    /api/v1/users/<uuid>/email - PATCH
    '''

    new_email = second_user.email

    url = resolve_url('api:update-email', user.uuid)

    resp = client_api_auth.patch(url, data={'email': new_email}, format='json')
    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert body['errors'] == ['Usuário com este Endereço de email já existe.']

    old_email = user.email
    user.refresh_from_db()
    new_email = user.email
    assert old_email == new_email

    assert user.email_verify


def test_fail_update_must_be_auth(client_api, user):
    '''
    /api/v1/users/<uuid>/email - PATCH
    '''

    new_email = 'user1_new@email.com'

    url = resolve_url('api:update-email', user.uuid)

    resp = client_api.patch(url, data={'email': new_email}, format='json')
    body = resp.json()

    assert resp.status_code == HTTPStatus.UNAUTHORIZED
    assert body['detail'] == 'As credenciais de autenticação não foram fornecidas.'
