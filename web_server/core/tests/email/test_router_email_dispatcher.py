from http import HTTPStatus
from uuid import uuid4

from django.shortcuts import resolve_url

from web_server.core.errors_msg import MSG_ERROR_TOKEN_USER

END_POINT = 'core:read-update-email'


def test_not_allowed_method(client_api_auth, user):

    url = resolve_url(END_POINT, user.uuid)

    resp = client_api_auth.post(url)
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    resp = client_api_auth.put(url)
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    resp = client_api_auth.delete(url)
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED


def test_allowed_method(client_api_auth, user):

    url = resolve_url(END_POINT, user.uuid)

    resp = client_api_auth.options(url)

    assert resp.status_code == HTTPStatus.OK

    options = map(str.strip, resp.headers['Allow'].split(','))

    assert set(options) == set(['OPTIONS', 'PATCH', 'GET'])


def test_update_email_token_id_and_user_id_dont_match(client_api_auth, user):

    url = resolve_url(END_POINT, uuid4())
    response = client_api_auth.patch(url)

    assert response.status_code == HTTPStatus.UNAUTHORIZED

    body = response.json()

    assert body['errors'] == MSG_ERROR_TOKEN_USER
