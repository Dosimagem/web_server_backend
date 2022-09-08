from http import HTTPStatus
from uuid import uuid4

import pytest
from django.shortcuts import resolve_url

from web_server.api.tests.conftest import HTTP_METHODS


def test_read_users_info_by_id(client_api, user):

    url = resolve_url('api:users', id=user.uuid)

    client_api.credentials(HTTP_AUTHORIZATION='Bearer ' + user.auth_token.key)
    response = client_api.get(url)

    assert response.status_code == HTTPStatus.OK

    body = response.json()

    assert body['email'] == user.email
    assert body['name'] == user.profile.name
    assert body['phone'] == user.profile.phone
    assert body['clinic'] == user.profile.clinic
    assert body['role'] == user.profile.role
    assert body['cpf'] == user.profile.cpf
    assert body['cnpj'] == user.profile.cnpj


def test_read_users_without_token(client_api):

    url = resolve_url('api:users', id=uuid4())

    response = client_api.get(url)

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Authentication credentials were not provided.'}


def test_read_users_wrong_token(client_api, db):

    url = resolve_url('api:users', id=uuid4())

    client_api.credentials(HTTP_AUTHORIZATION='Bearer ' + 'token')
    response = client_api.get(url)

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Invalid token.'}


@pytest.mark.parametrize("method", ['post', 'put', 'patch', 'delete'])
def test_read_users_not_allowed_method(method, user):
    http = HTTP_METHODS[method]

    header = {'HTTP_AUTHORIZATION': f'Bearer {user.auth_token.key}'}
    resp = http(resolve_url('api:users', id=user.uuid), **header)
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED
