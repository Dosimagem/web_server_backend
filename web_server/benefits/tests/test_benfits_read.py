from http import HTTPStatus
from uuid import uuid4

from django.shortcuts import resolve_url

from web_server.benefits.views import signature
from web_server.core.errors_msg import MSG_ERROR_TOKEN_USER

END_POINT = 'benefits:benefit-read'


# /api/v1/users/<uuid>/benefits/<uuid> - GET


def test_successfull(client_api_auth, user):

    url = resolve_url(END_POINT, user.uuid)

    resp = client_api_auth.get(url)
    body = resp.json()

    signature_db = signature

    assert resp.status_code == HTTPStatus.OK

    assert str(signature_db.id) == body['id']
    assert signature_db.benefits == body['benefits']
    assert signature_db.hired_period == body['hiredPeriod']
    assert signature_db.test_period == body['testPeriod']
    assert signature_db.price == body['price']
    assert signature_db.activated == body['activated']
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
    resp = client_api_auth.get(url)

    assert resp.status_code == HTTPStatus.UNAUTHORIZED

    body = resp.json()

    assert body['errors'] == MSG_ERROR_TOKEN_USER


def test_fail_must_be_auth(client_api, user):

    url = resolve_url(END_POINT, user.uuid)

    resp = client_api.get(url)
    body = resp.json()

    assert resp.status_code == HTTPStatus.UNAUTHORIZED
    assert body['detail'] == 'As credenciais de autenticação não foram fornecidas.'
