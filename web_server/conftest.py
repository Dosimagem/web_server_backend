import pytest
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from web_server.core.models import UserProfile

HTTP_METHODS = {
    'get': APIClient().get,
    'post': APIClient().post,
    'put': APIClient().put,
    'patch': APIClient().patch,
    'delete': APIClient().delete,
}


@pytest.fixture(autouse=True)
def disable_SQL_logging(settings):
    settings.LOGGER_SQL = False


@pytest.fixture(autouse=True)
def mediafiles(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path / 'media'


@pytest.fixture
def client_api():
    return APIClient()


@pytest.fixture
def client_api_auth(client_api, user):
    client_api.credentials(HTTP_AUTHORIZATION='Bearer ' + user.auth_token.key)
    return client_api


@pytest.fixture
def register_infos():
    return dict(
        # User
        email='test1@email.com',
        confirmed_email='test1@email.com',
        password1='123456!!',
        password2='123456!!',
        # Profile
        clinic='Clinica A',
        name='João Silva',
        cnpj='42438610000111',  # 42.438.610/0001-11
        cpf='93743851121',  # 937.438.511-21
        phone='55(33)1111-1111',
        role='Médico',
    )


@pytest.fixture
def user_info(register_infos):
    return dict(email=register_infos['email'], password=register_infos['password1'])


@pytest.fixture
def user_profile_info(register_infos):
    return {
        'name': register_infos['name'],
        'phone': register_infos['phone'],
        'clinic': register_infos['clinic'],
        'role': register_infos['role'],
        'cpf': register_infos['cpf'],
        'cnpj': register_infos['cnpj'],
    }


@pytest.fixture
def second_register_infos():
    return dict(
        # User
        email='test2@email.com',
        confirmed_email='test2@email.com',
        password1='123456!!',
        password2='123456!!',
        # Profile
        clinic='Clinica B',
        name='Maria Silva',
        cnpj='83398534000145',  # 83.398.534/0001-45
        cpf='52450318097',  # 524.503.180-97
        phone='55(41)22222-2222',
        role='Fisica médica',
    )


@pytest.fixture
def second_user_login_info(second_register_infos):
    return dict(
        email=second_register_infos['email'],
        password=second_register_infos['password1'],
    )


@pytest.fixture
def second_user_profile_info(second_register_infos):
    return {
        'name': second_register_infos['name'],
        'phone': second_register_infos['phone'],
        'clinic': second_register_infos['clinic'],
        'role': second_register_infos['role'],
        'cpf': second_register_infos['cpf'],
        'cnpj': second_register_infos['cnpj'],
    }


@pytest.fixture
def user(django_user_model, user_info, user_profile_info):
    user = django_user_model.objects.create_user(**user_info)
    user.email_verified = True
    user.save()
    UserProfile.objects.filter(user=user).update(**user_profile_info)
    Token.objects.create(user=user)
    return django_user_model.objects.get(id=user.id)


@pytest.fixture
def second_user(user, django_user_model, second_user_login_info, second_user_profile_info):
    new_user = django_user_model.objects.create_user(**second_user_login_info)
    UserProfile.objects.filter(user=new_user).update(**second_user_profile_info)
    Token.objects.create(user=new_user)
    return django_user_model.objects.get(id=new_user.id)
