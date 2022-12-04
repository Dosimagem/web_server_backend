from http import HTTPStatus

from dj_rest_auth.utils import jwt_encode
from django.shortcuts import resolve_url
from freezegun import freeze_time

from web_server.core.tests.conftest import asserts_cookie_tokens

URL_POINT = 'core:refresh_token'


@freeze_time('2022-01-01 00:00:00')
def test_refresh_token_ok(client_api, user):

    url = resolve_url(URL_POINT)

    _, refresh_token = jwt_encode(user)

    client_api.cookies.load({'jwt-refresh-token': refresh_token})
    resp = client_api.post(url)

    assert HTTPStatus.OK == resp.status_code

    asserts_cookie_tokens(resp)


def test_missing_token(client):

    url = resolve_url(URL_POINT)

    resp = client.post(url)

    assert HTTPStatus.UNAUTHORIZED == resp.status_code
    body = resp.json()

    expected = {'code': 'token_not_valid', 'detail': 'No valid refresh token found.'}

    assert expected == body


@freeze_time('2022-01-01', auto_tick_seconds=4 * 24 * 3600)
def test_refresh_token_expired(client, user):

    url = resolve_url(URL_POINT)

    _, refresh_token = jwt_encode(user)

    client.cookies.load({'jwt-refresh-token': refresh_token})
    resp = client.post(url)

    assert HTTPStatus.UNAUTHORIZED == resp.status_code

    body = resp.json()

    expected = {'code': 'token_not_valid', 'detail': 'Token is invalid or expired'}

    assert expected == body
