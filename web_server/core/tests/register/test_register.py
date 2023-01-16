from http import HTTPStatus

import pytest
from django.contrib.auth import get_user_model
from django.core import mail
from django.shortcuts import resolve_url
from freezegun import freeze_time

from web_server.conftest import HTTP_METHODS
from web_server.core.email import DOSIMAGEM_EMAIL
from web_server.core.tests.conftest import asserts_cookie_tokens

User = get_user_model()


pytestmark = pytest.mark.django_db


URL_REGISTER = resolve_url('core:register')


@freeze_time('2022-01-01 00:00:00')
def test_successfull_register(api_cnpj_successfull, client_api, register_infos):

    resp = client_api.post(URL_REGISTER, data=register_infos, format='json')

    user = User.objects.get(email=register_infos['email'])

    body = resp.json()

    assert body == {
        'id': str(user.uuid),
        'isStaff': user.is_staff,
    }

    assert resp.status_code == HTTPStatus.CREATED

    email = mail.outbox[0]

    assert 'Verificação de email da sua conta Dosimagem' == email.subject
    assert DOSIMAGEM_EMAIL == email.from_email
    assert [user.email] == email.to

    assert f'/users/{user.uuid}/email-confirm/?token={user.verification_email_secret}' in email.body
    assert user.sent_verification_email
    assert user.is_active
    assert not user.email_verified

    asserts_cookie_tokens(resp)


@freeze_time('2022-01-01 00:00:00')
def test_successfull_register_without_cpf_and_cnpj(client_api, register_infos_without_cpf_and_cnpj):

    resp = client_api.post(URL_REGISTER, data=register_infos_without_cpf_and_cnpj, format='json')

    user = User.objects.get(email=register_infos_without_cpf_and_cnpj['email'])

    body = resp.json()

    assert body == {
        'id': str(user.uuid),
        'isStaff': user.is_staff,
    }

    assert resp.status_code == HTTPStatus.CREATED

    email = mail.outbox[0]

    assert 'Verificação de email da sua conta Dosimagem' == email.subject
    assert DOSIMAGEM_EMAIL == email.from_email
    assert [user.email] == email.to

    assert f'/users/{user.uuid}/email-confirm/?token={user.verification_email_secret}' in email.body
    assert user.sent_verification_email
    assert user.is_active
    assert not user.email_verified

    asserts_cookie_tokens(resp)


def test_fail_user_unique_fields(client_api, user, register_infos):
    """
    Email
    """

    resp = client_api.post(URL_REGISTER, data=register_infos, format='json')

    errors_list = resp.json()['errors']

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    expected = 'email: Usuário com este Endereço de email já existe.'

    assert expected in errors_list


# TODO: Should the clinic name and CNPJ be unique?
def test_fail_profile_unique_fields(api_cnpj_successfull, client_api, user, second_register_infos):
    """
    Clinic, CPF and CNPJ.
    """

    second_register_infos['cpf'] = user.profile.cpf
    second_register_infos['clinic'] = user.profile.clinic
    second_register_infos['cnpj'] = user.profile.cnpj

    resp = client_api.post(URL_REGISTER, data=second_register_infos, format='json')

    errors_list = resp.json()['errors']

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    assert 'cpf: CPF já existe' in errors_list

    # assert 'Clínica já existe.' in errors_list
    # assert 'CNPJ já existe.' in errors_list


def test_fail_profile_invalid_cpf(api_cnpj_fail, client_api, second_register_infos):

    second_register_infos['cpf'] = '1'

    resp = client_api.post(URL_REGISTER, data=second_register_infos, format='json')

    errors_list = resp.json()['errors']

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    assert 'cpf: CPF inválido.' in errors_list


def test_fail_profile_invalid_cnpj(client_api, second_register_infos):

    second_register_infos['cnpj'] = '1'

    resp = client_api.post(URL_REGISTER, data=second_register_infos, format='json')

    errors_list = resp.json()['errors']

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    assert 'cnpj: CNPJ inválido.' in errors_list


def test_fail_profile_invalid_cnpj_api(api_cnpj_fail, client_api, second_register_infos):

    resp = client_api.post(URL_REGISTER, data=second_register_infos, format='json')

    errors_list = resp.json()['errors']

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    assert 'cnpj: CNPJ 83.398.534/0001-45 não encontrado.' in errors_list


def test_fail_profile_invalid_phone(api_cnpj_successfull, client_api, register_infos):

    register_infos['phone'] = '222'

    resp = client_api.post(URL_REGISTER, data=register_infos, format='json')

    errors_list = resp.json()['errors']

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    expected = 'phone: Introduza um número de telefone válido (ex. +12125552368).'

    assert expected in errors_list


def test_fail_profile_name_can_not_have_numbers(api_cnpj_successfull, client_api, register_infos):

    register_infos['name'] = 'Casas 2'

    resp = client_api.post(URL_REGISTER, data=register_infos, format='json')

    errors_list = resp.json()['errors']

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    expected = ['name: O nome não pode ter números.']

    assert expected == errors_list


def test_fail_profile_name_must_be_at_least_3_char(api_cnpj_successfull, client_api, register_infos):

    register_infos['name'] = 'ii'

    resp = client_api.post(URL_REGISTER, data=register_infos, format='json')

    errors_list = resp.json()['errors']

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    expected = ['name: Certifique-se de que o valor tenha no mínimo 3 caracteres (ele possui 2).']

    assert expected == errors_list


@pytest.mark.parametrize(
    'field, error',
    [
        (
            'email',
            [
                'email: Este campo é obrigatório.',
                'confirmed_email: Os dois campos de e-mail não correspondem.',
            ],
        ),
        ('confirmed_email', [('confirmed_email: Este campo é obrigatório.')]),
    ],
)
def test_register_missing_fields(client_api, field, error, register_infos):

    register_infos.pop(field)

    resp = client_api.post(URL_REGISTER, data=register_infos, format='json')

    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert body['errors'] == error


@pytest.mark.parametrize(
    'field, error',
    [
        ('name', ['name: Este campo é obrigatório.']),
        ('phone', ['phone: Este campo é obrigatório.']),
        ('clinic', ['clinic: Este campo é obrigatório.']),
        ('role', ['role: Este campo é obrigatório.']),
    ],
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

    assert 'email: Insira um endereço de email válido.' in errors_list

    expected = 'confirmed_email: Os dois campos de e-mail não correspondem.'

    assert expected in errors_list


def test_register_password_dont_mach(client_api, register_infos):

    register_infos['password2'] = register_infos['password1'] + '1'
    resp = client_api.post(URL_REGISTER, data=register_infos, format='json')

    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    expected = ['password2: Os dois campos de senha não correspondem.']

    assert body['errors'] == expected


def test_register_email_dont_mach(client_api, register_infos):

    register_infos['confirmed_email'] = register_infos['email'] + '1'
    resp = client_api.post(URL_REGISTER, data=register_infos, format='json')

    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    expected = ['confirmed_email: Os dois campos de e-mail não correspondem.']

    assert body['errors'] == expected


@pytest.mark.parametrize('method', ['get', 'put', 'patch', 'delete'])
def test_register_not_allowed_method(method):

    resp = HTTP_METHODS[method](URL_REGISTER, format='json')
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED
