from http import HTTPStatus

import pytest
from django.utils.translation import gettext as _
from django.contrib.auth import get_user_model
from django.shortcuts import resolve_url

from web_server.api.tests.conftest import HTTP_METHODS


User = get_user_model()


pytestmark = pytest.mark.django_db


URL_REGISTER = resolve_url('api:register')


def test_successfull_register(api_cnpj_successfull, client_api, register_infos):

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

    expected = 'Usuário com este Endereço de email já existe.'

    assert expected in errors_list


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

    assert 'Clínica já existe.' in errors_list
    assert 'CPF já existe.' in errors_list
    assert 'CNPJ já existe.' in errors_list


def test_fail_profile_invalid_cpf(api_cnpj_fail, client_api, second_register_infos):

    second_register_infos['cpf'] = '1'

    resp = client_api.post(URL_REGISTER, data=second_register_infos, format='json')

    errors_list = resp.json()['errors']

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    assert 'CPF inválido.' in errors_list


def test_fail_profile_invalid_cnpj(client_api, second_register_infos):

    second_register_infos['cnpj'] = '1'

    resp = client_api.post(URL_REGISTER, data=second_register_infos, format='json')

    errors_list = resp.json()['errors']

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    assert 'CNPJ inválido.' in errors_list


def test_fail_profile_invalid_cnpj_api(api_cnpj_fail, client_api, second_register_infos):
    '''
    Clinic, CPF and CNPJ.
    '''

    resp = client_api.post(URL_REGISTER, data=second_register_infos, format='json')

    errors_list = resp.json()['errors']

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    assert 'CNPJ 83.398.534/0001-45 não encontrado.' in errors_list


@pytest.mark.parametrize('field, error', [
    ('email', [
        'O campo email é obrigatório.',
        'Os campos emails não correspondem.'
        ]),
    ('confirmed_email', [
        ('O campo email de confirmação é obrigatório.')
        ]),
    ]
)
def test_register_missing_fields(client_api, field, error, register_infos):

    register_infos.pop(field)

    resp = client_api.post(URL_REGISTER, data=register_infos, format='json')

    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert body['errors'] == error


@pytest.mark.parametrize('field, error', [
    ('name', [
        'O campo nome é obrigatório.'
        ]),
    ('phone', [
        'O campo telefone é obrigatório.'
        ]),
    ('clinic', [
         'O campo clínica é obrigatório.'
        ]),
    ('role', [
         'O campo cargo é obrigatório.'
        ]),
    ('cpf', [
         'O campo CPF é obrigatório.'
        ])
    ]
)
def test_register_missing_profile_fields(api_cnpj_successfull, client_api, field, error, register_infos):

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

    expected = 'Os campos emails não correspondem.'

    assert expected in errors_list


def test_register_password_dont_mach(client_api, register_infos):

    register_infos['password2'] = register_infos['password1'] + '1'
    resp = client_api.post(URL_REGISTER, data=register_infos, format='json')

    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    expected = ['Os dois campos de senha não correspondem.']

    assert body['errors'] == expected


def test_register_email_dont_mach(client_api, register_infos):

    register_infos['confirmed_email'] = register_infos['email'] + '1'
    resp = client_api.post(URL_REGISTER, data=register_infos, format='json')

    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    expected = ['Os campos emails não correspondem.']

    assert body['errors'] == expected


@pytest.mark.parametrize("method", ['get', 'put', 'patch', 'delete'])
def test_register_not_allowed_method(method):

    resp = HTTP_METHODS[method](URL_REGISTER, format='json')
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED
