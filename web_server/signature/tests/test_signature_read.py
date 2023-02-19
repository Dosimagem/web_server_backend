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

    assert body['uuid'] == str(user_signature.uuid)
    assert body['plan'] == user_signature.plan
    assert body['hiredPeriod'] == user_signature.hired_period
    assert body['testPeriod'] == user_signature.test_period
    assert body['price'] == user_signature.price
    assert body['activated'] == user_signature.activated
    assert body['modality'] == user_signature.get_modality_display()
    assert body['discount'] == str(user_signature.discount)

    for e_db, e_resp in zip(user_signature.benefits.all(), body['benefits']):
        assert e_resp['uuid'] == str(e_db.uuid)
        assert e_resp['name'] == e_db.name
        assert e_resp['uri'] == e_db.uri

    # TODO: colocar a data de criação e update


def test_wrong_signature_id(client_api_auth, user):

    url = resolve_url(END_POINT, user.uuid, uuid4())

    resp = client_api_auth.get(url)

    assert resp.status_code == HTTPStatus.NOT_FOUND

    body = resp.json()

    assert body['errors'] == 'Assinatura não encontrada para esse usuário'


def test_signature_of_other_user(client_api_auth, user, second_user):

    sig = Signature.objects.create(user=second_user, plan='Pacote Dosimagem Anual', price='600.00')

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

    options = map(str.strip, resp.headers['Allow'].split(','))

    assert set(options) == set(['OPTIONS', 'GET'])


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
