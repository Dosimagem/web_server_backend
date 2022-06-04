import pytest


from web_server.users.forms import SignUpForm


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


def test_valid_form(user_form):
    form = SignUpForm(data=user_form)

    assert form.is_valid()


def test_password_ditnot_mach(user_form):
    user_form['password2'] = user_form['password1'] + '++'

    form = SignUpForm(data=user_form)

    assert not form.is_valid()

    expected = ['The two password fields didn’t match.']
    assert expected == form.errors['password2']
