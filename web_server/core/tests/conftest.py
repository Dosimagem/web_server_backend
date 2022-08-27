import pytest

# TODO: repensar essas fixtures


@pytest.fixture
def user_wrong_signup():
    return {'email': 'test@email.com',
            'confirmed_email': 'test_1@email.com',
            'password1': '123456!!!###',
            'password2': '123456!!!###++',
            'name': 'User Surname',
            'phone': '(11)999111213',
            'institution': 'Institution Asc',
            'role': 'Medico',
            }
