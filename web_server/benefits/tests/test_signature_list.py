from http import HTTPStatus
from uuid import uuid4

from django.shortcuts import resolve_url

from web_server.benefits.views import LIST_SIGNATURES
from web_server.core.errors_msg import MSG_ERROR_TOKEN_USER

END_POINT = 'signatures:signature-list'


# /api/v1/users/<uuid>/signature/ - GET


def test_successfull(client_api_auth, user):

    url = resolve_url(END_POINT, user.uuid)

    resp = client_api_auth.get(url)
    body = resp.json()

    signature_db = LIST_SIGNATURES

    assert resp.status_code == HTTPStatus.OK

    assert 3 == body['count']

    for expected, body_response in zip(signature_db, body['row']):
        assert str(expected.id) == body_response['id']
        assert expected.name == body_response['name']
        assert expected.benefits == body_response['benefits']
        assert expected.hired_period == body_response['hiredPeriod']
        assert expected.test_period == body_response['testPeriod']
        assert expected.price == body_response['price']
        assert expected.activated == body_response['activated']
        # TODO: colocar a data de criação e update


def test_list_not_allowed_method(client_api_auth, user):

    url = resolve_url(END_POINT, user.uuid)

    resp = client_api_auth.post(url)
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    resp = client_api_auth.put(url)
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    resp = client_api_auth.patch(url)
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    resp = client_api_auth.delete(url)
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED


def test_allowed_method(client_api_auth, user):

    url = resolve_url(END_POINT, user.uuid)

    resp = client_api_auth.options(url)

    assert resp.status_code == HTTPStatus.OK

    options = resp.headers['Allow'].split(',')

    for o in options:
        assert o.strip() in ['OPTIONS', 'GET']


def test_token_id_and_user_id_dont_match(client_api_auth, user):

    url = resolve_url(END_POINT, uuid4())
    response = client_api_auth.get(url)

    assert response.status_code == HTTPStatus.UNAUTHORIZED

    body = response.json()

    assert body['errors'] == MSG_ERROR_TOKEN_USER


def test_fail_must_be_auth(client_api, user):

    url = resolve_url(END_POINT, user.uuid)

    resp = client_api.get(url)
    body = resp.json()

    assert resp.status_code == HTTPStatus.UNAUTHORIZED
    assert body['detail'] == 'As credenciais de autenticação não foram fornecidas.'
