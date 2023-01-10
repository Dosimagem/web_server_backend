from http import HTTPStatus

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import resolve_url
from django.utils.translation import get_language
from django.utils.translation import gettext as _
from freezegun import freeze_time

from web_server.conftest import HTTP_METHODS
from web_server.core.tests.conftest import asserts_cookie_tokens

User = get_user_model()

URL_LOGIN = resolve_url('core:login')

pytestmark = pytest.mark.django_db


@freeze_time('2022-01-01 00:00:00')
def test_successfull_login(client_api, user_info, user):

    payload = {
        'username': user_info['email'],
        'password': user_info['password'],
    }

    resp = client_api.post(URL_LOGIN, data=payload, format='json')

    body = resp.json()

    assert resp.status_code == HTTPStatus.OK

    assert body['id'] == str(user.uuid)
    assert body['isStaff'] == user.is_staff

    asserts_cookie_tokens(resp)


def test_fail_wrong_username(client_api, user_info, user):

    payload = {
        'username': user_info['email'] + '1',
        'password': user_info['password'],
    }

    resp = client_api.post(URL_LOGIN, data=payload, format='json')

    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    assert body == {'errors': [_('Unable to log in with provided credentials.')]}


def test_fail_wrong_email(client_api, user_info, user):

    payload = {
        'username': user_info['email'] + '1',
        'password': user_info['password'],
    }

    resp = client_api.post(URL_LOGIN, data=payload, format='json')

    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    assert body == {'errors': [_('Unable to log in with provided credentials.')]}


def test_fail_login_missing_password(client_api, user_info):

    wrong_login = {'username': user_info['email']}
    resp = client_api.post(URL_LOGIN, data=wrong_login, format='json')
    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    expected = ['password: Este campo é obrigatório.']

    assert body == {'errors': expected}


@pytest.mark.parametrize('method', ['get', 'put', 'patch', 'delete'])
def test_login_not_allowed_method(method):

    resp = HTTP_METHODS[method](URL_LOGIN, format='json')

    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED
