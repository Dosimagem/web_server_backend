from http import HTTPStatus
from datetime import datetime

from jwt import decode
from jwt.exceptions import ExpiredSignatureError
from freezegun import freeze_time
from django.shortcuts import resolve_url

import pytest
from django.conf import settings


from web_server.core.views.register import _jwt_verification_email_secret


def test_token_expiration_time(user):

    initial_datetime = datetime(year=2000, month=1, day=1)

    with freeze_time(initial_datetime) as frozen_datetime:

        token = _jwt_verification_email_secret(user)

        payload = decode(token, settings.SECRET_KEY, algorithms=['HS256'])

        assert str(user.uuid) == payload['id']

        frozen_datetime.move_to('2000-1-2')

        with pytest.raises(ExpiredSignatureError):
            decode(token, settings.SECRET_KEY, algorithms=['HS256'])


def test_email_verify_success(client_api, user):

    url = resolve_url('core:email-verify')

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

    url = resolve_url('core:email-verify')

    user.verification_email_secret = _jwt_verification_email_secret(user)
    user.email_verified = False
    user.sent_verification_email = False
    user.save()

    resp = client_api.post(url, data={'token': user.verification_email_secret})

    assert HTTPStatus.CONFLICT == resp.status_code

    body = resp.json()

    assert {'error': ['Email de verificação ainda não foi enviado.']} == body


def test_fail_email_already_verified(client_api, user):

    url = resolve_url('core:email-verify')

    user.verification_email_secret = _jwt_verification_email_secret(user)
    user.email_verified = True
    user.sent_verification_email = True
    user.save()

    resp = client_api.post(url, data={'token': user.verification_email_secret})

    assert HTTPStatus.CONFLICT == resp.status_code

    body = resp.json()

    assert {'error': ['Email já foi verificado.']} == body


def test_fail_token_invalid(client_api, user):

    url = resolve_url('core:email-verify')

    user.email_verified = True
    user.sent_verification_email = True
    user.save()

    resp = client_api.post(url, data={'token': 'qwe'})

    assert HTTPStatus.BAD_REQUEST == resp.status_code

    body = resp.json()

    assert {'error': ['Token de verificação inválido ou expirado.']} == body


def test_missing_token(client_api, user):

    url = resolve_url('core:email-verify')

    user.email_verified = True
    user.sent_verification_email = True
    user.save()

    resp = client_api.post(url)

    assert HTTPStatus.BAD_REQUEST == resp.status_code

    body = resp.json()

    assert {'error': ['O campo token é obrigatório.']} == body


def test_fail_token_invalid(client_api, user):

    initial_datetime = datetime(year=2000, month=1, day=1)

    with freeze_time(initial_datetime) as frozen_datetime:

        url = resolve_url('core:email-verify')

        user.verification_email_secret = _jwt_verification_email_secret(user)
        user.email_verified = False
        user.sent_verification_email = True
        user.save()

        frozen_datetime.move_to('2000-1-2')

        resp = client_api.post(url, data={'token': user.verification_email_secret})

        assert HTTPStatus.CONFLICT == resp.status_code

        body = resp.json()

        assert {'error': ['Token de verificação inválido ou expirado.']} == body
