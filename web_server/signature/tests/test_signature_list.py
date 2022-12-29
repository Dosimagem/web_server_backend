from http import HTTPStatus
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.shortcuts import resolve_url

from web_server.core.errors_msg import MSG_ERROR_TOKEN_USER

User = get_user_model()


END_POINT = 'signatures:signature-list'


# /api/v1/users/<uuid>/signatures/ - GET


def test_successfull(client_api_auth, user, user_signature, user_other_signature):

    url = resolve_url(END_POINT, user.uuid)

    resp = client_api_auth.get(url)
    body = resp.json()

    signature_db = user.signatures.filter(user=user)

    assert resp.status_code == HTTPStatus.OK

    assert 2 == body['count']

    for expected, body_response in zip(signature_db, body['row']):
        assert str(expected.uuid) == body_response['uuid']
        assert expected.name == body_response['name']
        assert expected.hired_period == body_response['hiredPeriod']
        assert expected.test_period == body_response['testPeriod']
        assert str(expected.price) == body_response['price']
        assert expected.activated == body_response['activated']

        for e_b, e_r in zip(expected.benefits.all(), body_response['benefits']):
            assert str(e_b.uuid) == e_r['uuid']
            assert e_b.name == e_r['name']
            assert e_b.uri == e_r['uri']

        # TODO: colocar a data de criação e update


def test_user_not_have_signatures(client_api_auth, user):

    url = resolve_url(END_POINT, user.uuid)

    resp = client_api_auth.get(url)

    assert resp.status_code == HTTPStatus.OK

    body = resp.json()

    assert body['count'] == 0
    assert body['row'] == []


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
