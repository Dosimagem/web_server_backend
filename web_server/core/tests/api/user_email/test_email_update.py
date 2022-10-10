from http import HTTPStatus

from django.shortcuts import resolve_url


END_POINT = 'core:read-update-email'


def test_update(client_api_auth, user):
    '''
    /api/v1/users/<uuid>/email - PATCH
    '''

    new_email = 'user1_new@email.com'

    url = resolve_url(END_POINT, user.uuid)

    resp = client_api_auth.patch(url, data={'email': new_email}, format='json')
    assert resp.status_code == HTTPStatus.NO_CONTENT

    user.refresh_from_db()

    assert user.email == new_email

    assert not user.email_verified


def test_fail_update_invalid_email(client_api_auth, user):
    '''
    /api/v1/users/<uuid>/email - PATCH
    '''

    new_email = 'user1_newemail.com'

    url = resolve_url(END_POINT, user.uuid)

    resp = client_api_auth.patch(url, data={'email': new_email}, format='json')
    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert body['errors'] == ['Insira um endereço de email válido.']


def test_fail_update_email_must_be_unique(client_api_auth, user, second_user):
    '''
    /api/v1/users/<uuid>/email - PATCH
    '''

    new_email = second_user.email

    url = resolve_url(END_POINT, user.uuid)

    resp = client_api_auth.patch(url, data={'email': new_email}, format='json')
    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert body['errors'] == ['Usuário com este Endereço de email já existe.']

    old_email = user.email
    user.refresh_from_db()
    new_email = user.email
    assert old_email == new_email

    assert user.email_verified


def test_fail_update_must_be_auth(client_api, user):
    '''
    /api/v1/users/<uuid>/email - PATCH
    '''

    new_email = 'user1_new@email.com'

    url = resolve_url(END_POINT, user.uuid)

    resp = client_api.patch(url, data={'email': new_email}, format='json')
    body = resp.json()

    assert resp.status_code == HTTPStatus.UNAUTHORIZED
    assert body['detail'] == 'As credenciais de autenticação não foram fornecidas.'
