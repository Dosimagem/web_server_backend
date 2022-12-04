from http import HTTPStatus

import pytest
from django.shortcuts import resolve_url

URL_POINT = 'core:logout'

pytestmark = pytest.mark.django_db


def test_logout(client_api_auth_access_refresh):

    url = resolve_url(URL_POINT)

    resp = client_api_auth_access_refresh.post(url)

    assert HTTPStatus.OK == resp.status_code

    body = resp.json()

    assert {'detail': 'Logout.'} == body

    access_token = resp.cookies['jwt-access-token']
    refresh_token = resp.cookies['jwt-refresh-token']

    assert 'Thu, 01 Jan 1970 00:00:00 GMT' == access_token['expires']
    assert 'Thu, 01 Jan 1970 00:00:00 GMT' == refresh_token['expires']
