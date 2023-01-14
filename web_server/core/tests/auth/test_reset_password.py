from http import HTTPStatus

from django.core import mail
from django.shortcuts import resolve_url

from web_server.core.email import DOSIMAGEM_EMAIL

END_POINT = 'core:reset-password'


def test_send_reset_password(client_api, user):

    url = resolve_url(END_POINT)

    data = {'email': user.email}

    resp = client_api.post(url, data=data, format='json')

    assert HTTPStatus.OK == resp.status_code

    body = resp.json()

    assert body['message'] == 'E-mail enviado.'

    email = mail.outbox[0]

    assert 'Dosimagem - Resetando a senha' == email.subject
    assert DOSIMAGEM_EMAIL == email.from_email
    assert [user.email] == email.to

    user.refresh_from_db()

    assert f'/users/{user.uuid}/reset-password/?token={user.reset_password_secret}' in email.body
    assert user.sent_reset_password_email
    assert user.reset_password_secret
    assert user.is_active


def test_reset_password_missing_email(client_api, user):

    url = resolve_url(END_POINT)

    data = {}

    resp = client_api.post(url, data=data, format='json')

    assert HTTPStatus.BAD_REQUEST == resp.status_code

    body = resp.json()

    assert body['errors'] == ['email: Este campo é obrigatório.']

    assert not user.reset_password_secret
    assert not user.sent_reset_password_email


def test_reset_password_invalid_email(client_api, user):

    url = resolve_url(END_POINT)

    data = {'email': user.email.replace('@', '*')}

    resp = client_api.post(url, data=data, format='json')

    assert HTTPStatus.BAD_REQUEST == resp.status_code

    body = resp.json()

    assert body['errors'] == ['email: Insira um endereço de email válido.']

    assert not user.reset_password_secret
    assert not user.sent_reset_password_email


def test_rest_password_email_not_register(client_api, db):

    url = resolve_url(END_POINT)

    data = {'email': 'new_email@email.com'}

    resp = client_api.post(url, data=data, format='json')

    assert HTTPStatus.BAD_REQUEST == resp.status_code

    body = resp.json()

    assert body['errors'] == ['Este e-mail não está registrado.']


def test_not_allowed_method(client_api):

    url = resolve_url(END_POINT)

    resp = client_api.get(url, format='json')
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    resp = client_api.patch(url, format='json')
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    resp = client_api.put(url, format='json')
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    resp = client_api.delete(url, format='json')
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED


def test_allowed_method(client_api):

    url = resolve_url(END_POINT)

    resp = client_api.options(url)

    assert resp.status_code == HTTPStatus.OK

    options = map(str.strip, resp.headers['Allow'].split(','))

    assert set(options) == set(['OPTIONS', 'POST'])
