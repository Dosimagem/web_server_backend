from http import HTTPStatus
from uuid import uuid4

import pytest
from django.contrib.auth import get_user_model
from django.shortcuts import resolve_url
from django.utils.translation import gettext as _

from web_server.conftest import HTTP_METHODS
from web_server.core.errors_msg import MSG_ERROR_TOKEN_USER

User = get_user_model()


END_POINT = 'core:users-read-update'


def test_read_user_info_by_id(client_api, user):

    url = resolve_url(END_POINT, user_id=user.uuid)

    client_api.credentials(HTTP_AUTHORIZATION='Bearer ' + user.auth_token.key)
    response = client_api.get(url)

    assert response.status_code == HTTPStatus.OK

    body = response.json()

    assert body['email'] == user.email
    assert body['name'] == user.profile.name
    assert body['phone'] == user.profile.phone
    assert body['clinic'] == user.profile.clinic
    assert body['role'] == user.profile.role
    assert body['cpf'] == user.profile._cpf_mask()
    assert body['cnpj'] == user.profile._cnpj_mask()


def test_update_user_infos(api_cnpj_successfull, client_api_auth, user):

    url = resolve_url(END_POINT, user_id=user.uuid)

    payload = {
        'name': 'João Sliva Carvalho',
        'role': 'médico',
        'cnpj': '42438610000111',
        'clinic': 'Clinica A',
    }

    response = client_api_auth.patch(url, payload, format='json')

    assert response.status_code == HTTPStatus.NO_CONTENT

    user_db = User.objects.first()

    assert user_db.profile.name == 'João Sliva Carvalho'


def test_fail_update_user_infos_cnpj_with_mask(client_api_auth, user):

    url = resolve_url(END_POINT, user_id=user.uuid)

    payload = {
        'name': 'João Sliva Carvalho',
        'role': 'médico',
        'cnpj': '42.438.610/0001-11',
        'clinic': 'Clinica A',
    }

    response = client_api_auth.patch(url, payload, format='json')

    assert response.status_code == HTTPStatus.BAD_REQUEST

    body = response.json()

    expected = ['CNPJ inválido.']

    assert body['errors'] == expected


# TODO: Should the CNPJ be unique?
# def test_fail_update_user_infos_cnpj_unique_constrain(client_api_auth, user, second_user):

#     url = resolve_url(END_POINT, user_id=user.uuid)

#     payload = {
#         'name': 'João Sliva Carvalho',
#         'role': 'médico',
#         'cnpj': second_user.profile.cnpj,
#         'clinic': 'Clinica A'
#     }

#     response = client_api_auth.patch(url, payload, format='json')

#     assert response.status_code == HTTPStatus.BAD_REQUEST

#     body = response.json()

#     expected = ['CNPJ já existe.']

#     assert body['errors'] == expected

# TODO: Should the Clinic name be unique?
# def test_fail_update_user_infos_clinic_unique_constrain(api_cnpj_successfull, client_api_auth, user, second_user):

#     url = resolve_url(END_POINT, user_id=user.uuid)

#     payload = {
#         'name': 'João Sliva Carvalho',
#         'role': 'médico',
#         'cnpj': '42438610000111',
#         'clinic': second_user.profile.clinic
#     }

#     response = client_api_auth.patch(url, payload, format='json')

#     assert response.status_code == HTTPStatus.BAD_REQUEST

#     body = response.json()

#     expected = ['Clínica já existe.']

#     assert body['errors'] == expected


def test_read_update_user_without_token(client_api):

    url = resolve_url(END_POINT, user_id=uuid4())

    response = client_api.get(url)

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': _('Authentication credentials were not provided.')}


def test_read_update_user_wrong_token(client_api, user):

    url = resolve_url(END_POINT, user_id=user.uuid)

    client_api.credentials(HTTP_AUTHORIZATION='Bearer ' + 'token')
    response = client_api.get(url)

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': _('Invalid token.')}


def test_read_update_token_id_and_user_id_dont_match(client_api_auth, user, second_user):
    """
    /api/v1/users/<uuid> - GET, PATCH
    The token does not belong to the user
    """

    url = resolve_url(END_POINT, user_id=second_user.uuid)
    response = client_api_auth.get(url)

    assert response.status_code == HTTPStatus.UNAUTHORIZED

    body = response.json()

    assert body['errors'] == MSG_ERROR_TOKEN_USER


@pytest.mark.parametrize('method', ['post', 'put', 'delete'])
def test_read_update_user_not_allowed_method(method, user):
    http = HTTP_METHODS[method]

    header = {'HTTP_AUTHORIZATION': f'Bearer {user.auth_token.key}'}
    resp = http(resolve_url(END_POINT, user_id=user.uuid), **header)
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED
