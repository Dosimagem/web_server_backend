from datetime import datetime
from http import HTTPStatus
from uuid import uuid4

import pytest
from django.shortcuts import resolve_url
from freezegun import freeze_time

from web_server.conftest import fake
from web_server.core.email import _jwt_verification_email_secret

END_POINT = 'core:reset-password-confirm'


@pytest.fixture
def reset_email(user):

    token = _jwt_verification_email_secret(user)
    user.reset_password_secret = token
    user.sent_reset_password_email = True
    user.save()

    password = fake.password()

    return {'token': token, 'new_password1': password, 'new_password2': password}


def test_reset_password_confirm(client_api, user, reset_email):

    url = resolve_url(END_POINT, user.uuid)

    resp = client_api.post(url, data=reset_email, format='json')

    assert HTTPStatus.NO_CONTENT == resp.status_code

    user.refresh_from_db()

    assert user.check_password(reset_email['new_password1'])
    assert user.reset_password_secret is None
    assert not user.sent_reset_password_email


@pytest.mark.parametrize(
    'field, error',
    [
        ('token', ['token: Este campo é obrigatório.']),
        ('new_password1', ['new_password1: Este campo é obrigatório.']),
        ('new_password2', ['new_password2: Este campo é obrigatório.']),
    ],
)
def test_missing_fields(client_api, field, error, user, reset_email):

    url = resolve_url(END_POINT, user.uuid)

    reset_email.pop(field)

    resp = client_api.post(url, data=reset_email, format='json')

    assert HTTPStatus.BAD_REQUEST == resp.status_code

    body = resp.json()

    assert body['errors'] == error


def test_passwords_dont_mach(client_api, user, reset_email):

    reset_email['new_password1'] += '11'

    url = resolve_url(END_POINT, user.uuid)

    resp = client_api.post(url, data=reset_email, format='json')

    assert HTTPStatus.BAD_REQUEST == resp.status_code

    body = resp.json()

    assert body['errors'] == ['new_password2: Os dois campos da palavra-passe não coincidem.']


def test_wrong_user(client_api, reset_email):

    url = resolve_url(END_POINT, uuid4())

    resp = client_api.post(url, data=reset_email, format='json')

    assert HTTPStatus.BAD_REQUEST == resp.status_code

    body = resp.json()

    assert body['errors'] == ['Token de verificação inválido ou expirado para esse usuário.']


def test_fail_token_expired(client_api, user):
    """
    The Token must exipere after 24 h
    """

    initial_datetime = datetime(year=2000, month=1, day=1)

    with freeze_time(initial_datetime) as frozen_datetime:

        token = _jwt_verification_email_secret(user)
        user.reset_password_secret = token
        user.sent_reset_password_email = True
        user.save()

        password = fake.password()

        data = {'token': token, 'new_password1': password, 'new_password2': password}

        url = resolve_url(END_POINT, user.uuid)

        frozen_datetime.move_to('2000-1-2')

        resp = client_api.post(url, data=data)

        assert HTTPStatus.CONFLICT == resp.status_code

        body = resp.json()

        expected = {'errors': ['Token de verificação inválido ou expirado para esse usuário.']}

        assert expected == body


def test_user_in_url_is_different_to_user_in_jwt(client_api, user, second_user):

    url = resolve_url(END_POINT, user.uuid)

    token = _jwt_verification_email_secret(second_user)
    user.reset_password_secret = token
    user.sent_reset_password_email = True
    user.save()

    password = fake.password()

    data = {'token': token, 'new_password1': password, 'new_password2': password}

    resp = client_api.post(url, data=data)

    assert HTTPStatus.CONFLICT == resp.status_code

    body = resp.json()

    assert {'errors': ['Conflito no id do usuario.']} == body


def test_fail_token_used_twice(client_api, user, reset_email):

    url = resolve_url(END_POINT, user.uuid)

    resp = client_api.post(url, data=reset_email, format='json')

    assert HTTPStatus.NO_CONTENT == resp.status_code

    resp = client_api.post(url, data=reset_email, format='json')

    assert HTTPStatus.BAD_REQUEST == resp.status_code

    body = resp.json()

    assert {'errors': ['Token de verificação inválido ou expirado para esse usuário.']} == body


def test_fail_email_not_sent_yet(client_api, user, reset_email):

    url = resolve_url(END_POINT, user.uuid)

    user.sent_reset_password_email = False
    user.save()

    resp = client_api.post(url, data=reset_email)

    assert HTTPStatus.CONFLICT == resp.status_code

    body = resp.json()

    expected = {'errors': ['Email ainda não foi enviado.']}

    assert expected == body


def test_not_allowed_method(client_api, user):

    url = resolve_url(END_POINT, user.uuid)

    resp = client_api.get(url, format='json')
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    resp = client_api.patch(url, format='json')
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    resp = client_api.put(url, format='json')
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    resp = client_api.delete(url, format='json')
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED


def test_allowed_method(client_api, user):

    url = resolve_url(END_POINT, user.uuid)

    resp = client_api.options(url)

    assert resp.status_code == HTTPStatus.OK

    options = map(str.strip, resp.headers['Allow'].split(','))

    assert set(options) == set(['OPTIONS', 'POST'])
