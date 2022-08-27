from http import HTTPStatus

import pytest
from django.contrib.auth import get_user_model
from django.shortcuts import resolve_url
from rest_framework.test import APIClient


from web_server.api.views import _userToDict


User = get_user_model()

client = APIClient

CONTENT_TYPE = 'application/json'


HTTP_METHODS = {
    'get': client().get,
    'post': client().post,
    'put': client().put,
    'patch': client().patch,
    'delete': client().delete
}


pytestmark = pytest.mark.django_db


def test_succesuful_register(client, register_infos):

    response = client.post(resolve_url('api:register'), data=register_infos, content_type=CONTENT_TYPE)

    assert response.status_code == HTTPStatus.CREATED

    user = User.objects.first()

    body = response.json()

    assert body == _userToDict(user)


def test_fail_register_user_already_exist(client, register_infos):

    User.objects.create_user(email=register_infos['email'], password=register_infos['password1'])

    response = client.post(resolve_url('api:register'), data=register_infos, content_type=CONTENT_TYPE)

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'errors': ['User with this Email address already exists.']}


@pytest.mark.parametrize('field, error', [
    ('email', ['Email field is required.', 'The two email fields didn’t match.']),
    ('confirm_email', ['Confirm_email field is required.']),
    ('name', ['Name field is required.']),
    ('phone', ['Phone field is required.']),
    ('institution', ['Institution field is required.']),
    ('role', ['Role field is required.'])
    ]
)
def test_resgiter_missing_fields(field, error, client, register_infos):

    register_infos.pop(field)

    resp = client.post(resolve_url('api:register'), data=register_infos, content_type=CONTENT_TYPE)

    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert body['errors'] == error


def test_register_invalid_email(client, register_infos):

    register_infos['email'] = 'testmail.com'

    resp = client.post(resolve_url('api:register'), data=register_infos, content_type=CONTENT_TYPE)

    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert body['errors'] == ['Enter a valid email address.', 'The two email fields didn’t match.']


def test_register_password_dont_mach(client, register_infos):

    register_infos['password2'] = register_infos['password1'] + '1'
    resp = client.post(resolve_url('api:register'), data=register_infos, content_type=CONTENT_TYPE)

    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert body['errors'] == ['The two password fields didn’t match.']


def test_register_email_dont_mach(client, register_infos):

    register_infos['confirm_email'] = register_infos['email'] + '1'
    resp = client.post(resolve_url('api:register'), data=register_infos, content_type=CONTENT_TYPE)

    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert body['errors'] == ['The two email fields didn’t match.']


@pytest.mark.parametrize("method", ['get', 'put', 'patch', 'delete'])
def test_register_not_allowed_method(method):

    resp = HTTP_METHODS[method](resolve_url('api:register'), content_type=CONTENT_TYPE)
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED
