import pytest

from django.contrib.auth import get_user_model
from web_server.core.models import UserProfile


User = get_user_model()


# TODO: repensar essas fixtures

@pytest.fixture
def user_wrong_signup():
    return {'email': 'test@email.com',
            'confirm_email': 'test_1@email.com',
            'password1': '123456!!!###',
            'password2': '123456!!!###++',
            'name': 'User Surname',
            'phone': '(11)999111213',
            'institution': 'Institution Asc',
            'role': 'Medico',
            }


@pytest.fixture
def user_info():
    return {'email': 'test@email.com', 'password': '123456'}


@pytest.fixture
def user_profile_info():
    return {'name': 'User Surname',
            'phone': '(11)999111213',
            'institution': 'Institution Asc',
            'role': 'Medico'
            }


@pytest.fixture
def user(user_info, user_profile_info, db):
    user = User.objects.create(**user_info)
    UserProfile.objects.update(**user_profile_info)

    return user
