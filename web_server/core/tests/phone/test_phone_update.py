from http import HTTPStatus

from django.shortcuts import resolve_url

END_POINT = 'core:read-update-phone'

# /api/v1/users/<uuid>/phone/ - PATCH


def test_susuccessful(client_api_auth, user):

    url = resolve_url(END_POINT, user.uuid)

    resp = client_api_auth.patch(url, data={'phone': '+552122814433'}, format='json')

    assert resp.status_code == HTTPStatus.NO_CONTENT

    user.refresh_from_db()

    assert str(user.profile.phone) == '+552122814433'


def test_missing_fields(client_api_auth, user):

    url = resolve_url(END_POINT, user.uuid)

    resp = client_api_auth.patch(url, data={}, format='json')

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    body = resp.json()

    assert body['errors'] == ['phone: Este campo é obrigatório.']


def test_fail_update_invalid_phone(client_api_auth, user):

    url = resolve_url(END_POINT, user.uuid)

    resp = client_api_auth.patch(url, data={'phone': '2122814433'}, format='json')

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    body = resp.json()

    assert body['errors'] == ['phone: Informe um número de telefone válido.']


def test_fail_update_must_be_auth(client_api, user):

    url = resolve_url(END_POINT, user.uuid)

    resp = client_api.patch(url, data={'phone': '+552122814433'}, format='json')
    body = resp.json()

    assert resp.status_code == HTTPStatus.UNAUTHORIZED
    assert body['detail'] == 'As credenciais de autenticação não foram fornecidas.'
