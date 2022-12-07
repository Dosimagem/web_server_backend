from http import HTTPStatus

import pytest
from django.shortcuts import resolve_url

END_POINT = 'core:logout'

pytestmark = pytest.mark.django_db


def test_logout(client_api_auth_access_refresh):

    url = resolve_url(END_POINT)

    resp = client_api_auth_access_refresh.get(url)

    assert HTTPStatus.OK == resp.status_code

    body = resp.json()

    assert {'detail': 'Logout.'} == body

    access_token = resp.cookies['jwt-access-token']
    refresh_token = resp.cookies['jwt-refresh-token']

    assert 'Thu, 01 Jan 1970 00:00:00 GMT' == access_token['expires']
    assert 'Thu, 01 Jan 1970 00:00:00 GMT' == refresh_token['expires']


def test_not_allowed_method(client_api_auth, user):

    url = resolve_url(END_POINT)

    resp = client_api_auth.patch(url, format='json')
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    resp = client_api_auth.put(url, format='json')
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    resp = client_api_auth.delete(url, format='json')
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED


def test_allowed_method(client_api_auth, user):

    url = resolve_url(END_POINT)

    resp = client_api_auth.options(url)

    assert resp.status_code == HTTPStatus.OK

    options = resp.headers['Allow'].split(',')

    for o in options:
        assert o.strip() in ['OPTIONS', 'GET', 'POST', 'HEAD']
