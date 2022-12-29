from http import HTTPStatus
from uuid import uuid4

from django.shortcuts import resolve_url

from web_server.core.errors_msg import MSG_ERROR_TOKEN_USER
from web_server.signature.models import Signature

END_POINT = 'signatures:signature-read'


# /api/v1/users/<uuid>/signatures/<uuid> - GET


def test_successfull(client_api_auth, user, user_signature):

    url = resolve_url(END_POINT, user.uuid, user_signature.uuid)

    resp = client_api_auth.get(url)
    body = resp.json()

    assert resp.status_code == HTTPStatus.OK

    assert str(user_signature.uuid) == body['uuid']
    assert user_signature.name == body['name']
    assert user_signature.hired_period == body['hiredPeriod']
    assert user_signature.test_period == body['testPeriod']
    assert user_signature.price == body['price']
    assert user_signature.activated == body['activated']

    for e_b, e_r in zip(user_signature.benefits.all(), body['benefits']):
        assert str(e_b.uuid) == e_r['uuid']
        assert e_b.name == e_r['name']
        assert e_b.uri == e_r['uri']

    # TODO: colocar a data de criação e update


def test_wrong_signature_id(client_api_auth, user):

    url = resolve_url(END_POINT, user.uuid, uuid4())

    resp = client_api_auth.get(url)

    assert resp.status_code == HTTPStatus.NOT_FOUND

    body = resp.json()

    assert body['errors'] == 'Assinatura não encontrada para esse usuário'


def test_signature_of_other_user(client_api_auth, user, second_user):

    sig = Signature.objects.create(user=second_user, name='Pacote Dosimagem Anual', price='600.00')

    url = resolve_url(END_POINT, user.uuid, sig.uuid)

    resp = client_api_auth.get(url)

    assert resp.status_code == HTTPStatus.NOT_FOUND

    body = resp.json()

    assert body['errors'] == 'Assinatura não encontrada para esse usuário'


def test_list_not_allowed_method(client_api_auth, user):

    url = resolve_url(END_POINT, user.uuid, uuid4())

    resp = client_api_auth.post(url)
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    resp = client_api_auth.put(url)
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    resp = client_api_auth.patch(url)
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    resp = client_api_auth.delete(url)
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED


def test_allowed_method(client_api_auth, user):

    url = resolve_url(END_POINT, user.uuid, uuid4())

    resp = client_api_auth.options(url)

    assert resp.status_code == HTTPStatus.OK

    options = resp.headers['Allow'].split(',')

    for o in options:
        assert o.strip() in ['OPTIONS', 'GET']


def test_token_id_and_user_id_dont_match(client_api_auth, user):

    url = resolve_url(END_POINT, uuid4(), uuid4())
    resp = client_api_auth.get(url)

    assert resp.status_code == HTTPStatus.UNAUTHORIZED

    body = resp.json()

    assert body['errors'] == MSG_ERROR_TOKEN_USER


def test_fail_must_be_auth(client_api, user):

    url = resolve_url(END_POINT, user.uuid, uuid4())

    resp = client_api.get(url)
    body = resp.json()

    assert resp.status_code == HTTPStatus.UNAUTHORIZED
    assert body['detail'] == 'As credenciais de autenticação não foram fornecidas.'
