from http import HTTPStatus
from uuid import uuid4

from django.core import mail
from django.shortcuts import resolve_url

from web_server.core.email import DOSIMAGEM_EMAIL
from web_server.core.errors_msg import MSG_ERROR_TOKEN_USER

END_POINT = 'core:email-resend'


# /api/v1/users/<uuid>/email/resend - POST


def test_resend(client_api_auth, user):

    url = resolve_url(END_POINT, user.uuid)

    resp = client_api_auth.post(url)
    assert resp.status_code == HTTPStatus.NO_CONTENT

    user.refresh_from_db()

    email = mail.outbox[0]

    assert 'Verificação de email da sua conta Dosimagem' == email.subject
    assert DOSIMAGEM_EMAIL == email.from_email
    assert [user.email] == email.to

    assert f'/users/{user.uuid}/email-confirm/?token={user.verification_email_secret}' in email.body
    assert user.sent_verification_email
    assert not user.email_verified
    assert user.verification_email_secret


def test_fail_must_be_auth(client_api, user):

    url = resolve_url(END_POINT, user.uuid)

    resp = client_api.post(url)
    body = resp.json()

    assert resp.status_code == HTTPStatus.UNAUTHORIZED
    assert body['detail'] == 'As credenciais de autenticação não foram fornecidas.'


def test_token_id_and_user_id_dont_match(client_api_auth, user):

    url = resolve_url(END_POINT, uuid4())
    response = client_api_auth.post(url)

    assert response.status_code == HTTPStatus.UNAUTHORIZED

    body = response.json()

    assert body['errors'] == MSG_ERROR_TOKEN_USER


def test_wrong_token(client_api, user):

    url = resolve_url(END_POINT, user_id=user.uuid)

    client_api.cookies.load({'jwt-access-token': 'token'})
    response = client_api.post(url)

    expected = {
        'code': 'token_not_valid',
        'detail': 'O token fornecido não é válido para nenhum tipo de token',
        'messages': [{'message': 'O token é inválido ou expirou', 'tokenClass': 'AccessToken', 'tokenType': 'access'}],
    }

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == expected
