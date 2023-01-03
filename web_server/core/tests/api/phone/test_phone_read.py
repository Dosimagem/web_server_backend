from http import HTTPStatus

from django.shortcuts import resolve_url

END_POINT = 'core:read-update-phone'

# /api/v1/users/<uuid>/phone/ - GET


def test_successful(client_api_auth, user):

    url = resolve_url(END_POINT, user.uuid)

    resp = client_api_auth.get(url)

    assert resp.status_code == HTTPStatus.OK

    body = resp.json()

    assert body == {'phone': user.profile.phone_str}


def test_fail_update_must_be_auth(client_api, user):

    url = resolve_url(END_POINT, user.uuid)

    resp = client_api.get(url)
    body = resp.json()

    assert resp.status_code == HTTPStatus.UNAUTHORIZED
    assert body['detail'] == 'As credenciais de autenticação não foram fornecidas.'
