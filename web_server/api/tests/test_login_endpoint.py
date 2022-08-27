from http import HTTPStatus

import pytest
from django.contrib.auth import get_user_model
from django.shortcuts import resolve_url

from web_server.api.tests.conftest import HTTP_METHODS


User = get_user_model()

URL_LOGIN = resolve_url('api:login')

pytestmark = pytest.mark.django_db


def test_successfull_login(client_api, user_info, user):

    payload = {
        'username': user_info['email'],
        'password': user_info['password']
    }

    response = client_api.post(URL_LOGIN, data=payload, format='json')

    body = response.json()

    assert response.status_code == HTTPStatus.OK

    assert body['id'] == str(user.uuid)
    assert body['token'] == user.auth_token.key
    assert body['is_staff'] == user.is_staff


def test_fail_wrong_username(client_api, user_info, user):

    payload = {
        'username': user_info['email'] + '1',
        'password': user_info['password']
    }

    response = client_api.post(URL_LOGIN, data=payload, format='json')

    body = response.json()

    assert response.status_code == HTTPStatus.BAD_REQUEST

    assert body == {'errors': ['Unable to log in with provided credentials.']}


def test_fail_wrong_email(client_api, user_info, user):

    payload = {
        'username': user_info['email'] + '1',
        'password': user_info['password']
    }

    response = client_api.post(URL_LOGIN, data=payload, format='json')

    body = response.json()

    assert response.status_code == HTTPStatus.BAD_REQUEST

    assert body == {'errors': ['Unable to log in with provided credentials.']}


def test_fail_login_missing_password(client_api, user_info):

    wrong_login = {'username': user_info['email']}
    resp = client_api.post(URL_LOGIN, data=wrong_login, format='json')
    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    assert body == {'errors': ['Password field is required.']}


def test_fail_login_missing_username(client_api, user_info):

    wrong_login = {'password': user_info['password']}
    resp = client_api.post(URL_LOGIN, data=wrong_login, format='json')
    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert body == {'errors': ['Username field is required.']}


def test_fail_login_missing_username_and_password(client_api):

    wrong_login = {}
    resp = client_api.post(URL_LOGIN, data=wrong_login, format='json')
    response_dict = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert response_dict == {'errors': ['Username field is required.', 'Password field is required.']}


@pytest.mark.parametrize("method", ['get', 'put', 'patch', 'delete'])
def test_login_not_allowed_method(method):

    resp = HTTP_METHODS[method](URL_LOGIN, format='json')
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED
