from http import HTTPStatus

import pytest
from django.contrib.auth import get_user_model
from django.shortcuts import resolve_url

from web_server.api.tests.conftest import HTTP_METHODS


User = get_user_model()


pytestmark = pytest.mark.django_db


URL_REGISTER = resolve_url('api:register')


def test_successfull_register(client_api, register_infos):

    response = client_api.post(URL_REGISTER, data=register_infos, format='json')

    assert response.status_code == HTTPStatus.CREATED

    user = User.objects.first()

    body = response.json()

    assert body == {'id': str(user.uuid), 'token': user.auth_token.key, 'isStaff': user.is_staff}


def test_fail_register_user_already_exist(client_api, register_infos):

    User.objects.create_user(email=register_infos['email'], password=register_infos['password1'])

    response = client_api.post(URL_REGISTER, data=register_infos, format='json')

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'errors': ['User with this Email address already exists.']}


@pytest.mark.parametrize('field, error', [
    ('email', ['Email field is required.', 'The two email fields didn’t match.']),
    ('confirmed_email', ['Confirmed_email field is required.']),
    ('name', ['Name field is required.']),
    ('phone', ['Phone field is required.']),
    ('institution', ['Institution field is required.']),
    ('role', ['Role field is required.'])
    ]
)
def test_resgiter_missing_fields(client_api, field, error, register_infos):

    register_infos.pop(field)

    resp = client_api.post(URL_REGISTER, data=register_infos, format='json')

    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert body['errors'] == error


def test_register_invalid_email(client_api, register_infos):

    register_infos['email'] = 'testmail.com'

    resp = client_api.post(URL_REGISTER, data=register_infos, format='json')

    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert body['errors'] == ['Enter a valid email address.', 'The two email fields didn’t match.']


def test_register_password_dont_mach(client_api, register_infos):

    register_infos['password2'] = register_infos['password1'] + '1'
    resp = client_api.post(URL_REGISTER, data=register_infos, format='json')

    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert body['errors'] == ['The two password fields didn’t match.']


def test_register_email_dont_mach(client_api, register_infos):

    register_infos['confirmed_email'] = register_infos['email'] + '1'
    resp = client_api.post(URL_REGISTER, data=register_infos, format='json')

    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert body['errors'] == ['The two email fields didn’t match.']


@pytest.mark.parametrize("method", ['get', 'put', 'patch', 'delete'])
def test_register_not_allowed_method(method):

    resp = HTTP_METHODS[method](URL_REGISTER, format='json')
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED
