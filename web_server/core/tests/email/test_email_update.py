from http import HTTPStatus

from django.core import mail
from django.shortcuts import resolve_url

from web_server.core.email import DOSIMAGEM_EMAIL

END_POINT = 'core:read-update-email'


# /api/v1/users/<uuid>/email/ - PATCH


def test_update(client_api_auth, user):

    new_email = 'user1_new@email.com'

    url = resolve_url(END_POINT, user.uuid)

    resp = client_api_auth.patch(url, data={'email': new_email}, format='json')
    assert resp.status_code == HTTPStatus.NO_CONTENT

    user.refresh_from_db()

    assert user.email == new_email

    email = mail.outbox[0]

    assert 'Verificação de email da sua conta Dosimagem' == email.subject
    assert DOSIMAGEM_EMAIL == email.from_email
    assert [user.email] == email.to

    assert f'/users/{user.uuid}/email-confirm/?token={user.verification_email_secret}' in email.body
    assert user.sent_verification_email
    assert not user.email_verified


def test_fail_update_invalid_email(client_api_auth, user):

    new_email = 'user1_newemail.com'

    url = resolve_url(END_POINT, user.uuid)

    resp = client_api_auth.patch(url, data={'email': new_email}, format='json')
    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert body['errors'] == ['email: Insira um endereço de email válido.']


def test_fail_update_email_must_be_unique(client_api_auth, user, second_user):

    new_email = second_user.email

    url = resolve_url(END_POINT, user.uuid)

    resp = client_api_auth.patch(url, data={'email': new_email}, format='json')
    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert body['errors'] == ['email: Usuário com este Endereço de email já existe.']

    old_email = user.email
    user.refresh_from_db()
    new_email = user.email
    assert old_email == new_email

    assert user.email_verified


def test_fail_update_must_be_auth(client_api, user):

    new_email = 'user1_new@email.com'

    url = resolve_url(END_POINT, user.uuid)

    resp = client_api.patch(url, data={'email': new_email}, format='json')
    body = resp.json()

    assert resp.status_code == HTTPStatus.UNAUTHORIZED
    assert body['detail'] == 'As credenciais de autenticação não foram fornecidas.'
