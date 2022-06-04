import pytest


@pytest.fixture
def user_form(db):
    return {"username": "User",
            "phone": "(11)999111213",
            "email": "test@email.com",
            "institution": "Institution_A",
            "role": "Engineer",
            "password1": "123456!!!###",
            "password2": "123456!!!###"
            }


@pytest.fixture
def user_form_wrong_password(db):
    return {"username": "User",
            "phone": "(11)999111213",
            "email": "test@email.com",
            "institution": "Institution_A",
            "role": "Engineer",
            "password1": "123456!!!###",
            "password2": "123456!!!###++"
            }
