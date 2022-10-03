from http import HTTPStatus

from django.shortcuts import resolve_url


def test_read(client_api_auth, user):
    '''
    /api/v1/users/<uuid>/email - GET
    '''

    url = resolve_url('api:read-update-email', user.uuid)
    resp = client_api_auth.get(url)
    body = resp.json()

    assert resp.status_code == HTTPStatus.OK

    user.refresh_from_db()

    assert user.email == body['email']
    assert user.email_verified == body['verified']


def test_fail_read_must_be_auth(client_api, user):
    '''
    /api/v1/users/<uuid>/email - GET
    '''

    url = resolve_url('api:read-update-email', user.uuid)

    resp = client_api.get(url)
    body = resp.json()

    assert resp.status_code == HTTPStatus.UNAUTHORIZED
    assert body['detail'] == 'As credenciais de autenticação não foram fornecidas.'
