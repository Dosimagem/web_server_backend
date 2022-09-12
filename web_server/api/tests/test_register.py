from http import HTTPStatus

import pytest
from django.utils.translation import gettext as _
from django.contrib.auth import get_user_model
from django.shortcuts import resolve_url
from rest_framework.authtoken.models import Token

from web_server.api.tests.conftest import HTTP_METHODS


User = get_user_model()


pytestmark = pytest.mark.django_db


URL_REGISTER = resolve_url('api:register')


def test_successfull_register(client_api, register_infos):

    resp = client_api.post(URL_REGISTER, data=register_infos, format='json')

    assert resp.status_code == HTTPStatus.CREATED

    user = User.objects.first()

    body = resp.json()

    assert body == {'id': str(user.uuid), 'token': user.auth_token.key, 'isStaff': user.is_staff}


def test_fail_user_unique_fields(client_api, user, register_infos):
    '''
    Email
    '''

    resp = client_api.post(URL_REGISTER, data=register_infos, format='json')

    errors_list = resp.json()['errors']

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    assert _('User with this Email address already exists.') in errors_list


def test_fail_profile_unique_fields(client_api, user, second_register_infos):
    '''
    Clinic, CPF and CNPJ.
    '''

    second_register_infos['clinic'] = user.profile.clinic
    second_register_infos['cpf'] = user.profile.cpf
    second_register_infos['cnpj'] = user.profile.cnpj

    resp = client_api.post(URL_REGISTER, data=second_register_infos, format='json')

    errors_list = resp.json()['errors']

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    assert _('Clinic already exists') in errors_list
    assert _('CPF already exists') in errors_list
    assert _('CNPJ already exists') in errors_list


def test_when_profile_fail_the_user_must_not_be_create(client_api, user, second_register_infos):
    '''
    Clinic, CPF and CNPJ.
    '''

    second_register_infos['clinic'] = user.profile.clinic

    resp = client_api.post(URL_REGISTER, data=second_register_infos, format='json')

    errors_list = resp.json()['errors']

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    assert User.objects.count() == 1
    assert Token.objects.count() == 1

    assert _('Clinic already exists') in errors_list


@pytest.mark.parametrize('field, error', [
    ('email', [_('Email field is required.'), _('The two email fields didn’t match.')]),
    ('confirmed_email', [_('Confirmed_email field is required.')]),
    ('name', [_('Name field is required.')]),
    ('phone', [_('Phone field is required.')]),
    ('clinic', [_('Clinic field is required.')]),
    ('role', [_('Role field is required.')])
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

    errors_list = resp.json()['errors']

    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert _('Enter a valid email address.') in errors_list
    assert _('The two email fields didn’t match.') in errors_list


def test_register_password_dont_mach(client_api, register_infos):

    register_infos['password2'] = register_infos['password1'] + '1'
    resp = client_api.post(URL_REGISTER, data=register_infos, format='json')

    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert body['errors'] == [_('The two password fields didn’t match.')]


def test_register_email_dont_mach(client_api, register_infos):

    register_infos['confirmed_email'] = register_infos['email'] + '1'
    resp = client_api.post(URL_REGISTER, data=register_infos, format='json')

    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert body['errors'] == [_('The two email fields didn’t match.')]


@pytest.mark.parametrize("method", ['get', 'put', 'patch', 'delete'])
def test_register_not_allowed_method(method):

    resp = HTTP_METHODS[method](URL_REGISTER, format='json')
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED
