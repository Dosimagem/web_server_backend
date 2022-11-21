from datetime import datetime
from http import HTTPStatus
from uuid import uuid4

from django.shortcuts import resolve_url
from freezegun import freeze_time

from web_server.core.email import _jwt_verification_email_secret

END_POINT = 'core:email-verify'


def test_email_verify_success(client_api, user):

    url = resolve_url(END_POINT, user.uuid)

    user.verification_email_secret = _jwt_verification_email_secret(user)
    user.email_verified = False
    user.sent_verification_email = True
    user.save()

    resp = client_api.post(url, data={'token': user.verification_email_secret})

    assert HTTPStatus.OK == resp.status_code

    body = resp.json()

    assert {'message': 'Email verificado.'} == body

    user.refresh_from_db()

    assert user.email_verified


def test_fail_verify_email_not_sent_yet(client_api, user):

    url = resolve_url(END_POINT, user.uuid)

    user.verification_email_secret = _jwt_verification_email_secret(user)
    user.email_verified = False
    user.sent_verification_email = False
    user.save()

    resp = client_api.post(url, data={'token': user.verification_email_secret})

    assert HTTPStatus.CONFLICT == resp.status_code

    body = resp.json()

    assert {'errors': ['Email de verificação ainda não foi enviado.']} == body


def test_fail_email_already_verified(client_api, user):

    url = resolve_url(END_POINT, user.uuid)

    user.verification_email_secret = _jwt_verification_email_secret(user)
    user.email_verified = True
    user.sent_verification_email = True
    user.save()

    resp = client_api.post(url, data={'token': user.verification_email_secret})

    assert HTTPStatus.CONFLICT == resp.status_code

    body = resp.json()

    assert {'errors': ['Email já foi verificado.']} == body


def test_fail_token_used_twice(client_api, user):

    url = resolve_url(END_POINT, user.uuid)

    user.verification_email_secret = _jwt_verification_email_secret(user)
    user.email_verified = False
    user.sent_verification_email = True
    user.save()

    resp = client_api.post(url, data={'token': user.verification_email_secret})

    assert HTTPStatus.OK == resp.status_code

    resp = client_api.post(url, data={'token': user.verification_email_secret})

    assert HTTPStatus.BAD_REQUEST == resp.status_code

    body = resp.json()

    assert {'errors': ['Token de verificação inválido ou expirado.']} == body


def test_fail_token_invalid(client_api, user):

    url = resolve_url(END_POINT, user.uuid)

    user.email_verified = True
    user.sent_verification_email = True
    user.save()

    resp = client_api.post(url, data={'token': 'qwe'})

    assert HTTPStatus.BAD_REQUEST == resp.status_code

    body = resp.json()

    assert {'errors': ['Token de verificação inválido ou expirado.']} == body


def test_missing_token(client_api, user):

    url = resolve_url(END_POINT, user.uuid)

    user.email_verified = True
    user.sent_verification_email = True
    user.save()

    resp = client_api.post(url)

    assert HTTPStatus.BAD_REQUEST == resp.status_code

    body = resp.json()

    assert {'errors': ['O campo token é obrigatório.']} == body


def test_fail_token_expired(client_api, user):

    initial_datetime = datetime(year=2000, month=1, day=1)

    with freeze_time(initial_datetime) as frozen_datetime:

        url = resolve_url(END_POINT, user.uuid)

        user.verification_email_secret = _jwt_verification_email_secret(user)
        user.email_verified = False
        user.sent_verification_email = True
        user.save()

        frozen_datetime.move_to('2000-1-2')

        resp = client_api.post(url, data={'token': user.verification_email_secret})

        assert HTTPStatus.CONFLICT == resp.status_code

        body = resp.json()

        assert {'errors': ['Token de verificação inválido ou expirado.']} == body


def test_allowed_method(client_api, user):

    url = resolve_url(END_POINT, user.uuid)

    resp = client_api.options(url)

    assert resp.status_code == HTTPStatus.OK

    options = resp.headers['Allow'].split(',')

    for o in options:
        assert o.strip() in ['OPTIONS', 'POST']


def test_user_in_url_is_different_to_user_in_jwt(client_api, user):
    url = resolve_url(END_POINT, uuid4())

    user.verification_email_secret = _jwt_verification_email_secret(user)
    user.email_verified = False
    user.sent_verification_email = True
    user.save()

    resp = client_api.post(url, data={'token': user.verification_email_secret})

    assert HTTPStatus.CONFLICT == resp.status_code

    body = resp.json()

    assert {'errors': ['Conflito no id do usuario.']} == body
