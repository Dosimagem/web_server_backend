import pytest

from django.contrib.auth import get_user_model

from web_server.core.models import UserProfile


User = get_user_model()


@pytest.fixture
def user_form():
    return {'email': 'test@email.com',
            'password1': '123456!!!###',
            'password2': '123456!!!###'
            }


@pytest.fixture
def user_form_wrong_password():
    return {'email': 'test@email.com',
            'password1': '123456!!!###',
            'password2': '123456!!!###++'
            }


@pytest.fixture
def user_info():
    return { 'email': 'test@email.com',
             'password': '123456',
            }


@pytest.fixture
def user_profile_info():
    return {'name': 'User 1',
            'phone': '(11)999111213',
            'institution': 'Institution_A',
            'role': 'Engineer',
            }

@pytest.fixture
def user(user_info, user_profile_info, db):
    user = User.objects.create(**user_info)
    UserProfile.objects.create(**user_profile_info, user=user)

    return user
