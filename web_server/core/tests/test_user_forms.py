import pytest
from web_server.core.forms import UserForm


def test_valid_user_form(user_form, db):

    form = UserForm(data=user_form)

    assert form.is_valid()


@pytest.mark.parametrize(
    'field',
    ['email', 'password1', 'password2'],
)
def test_field_is_not_optional(user_form, field, db):

    del user_form[field]
    form = UserForm(data=user_form)

    assert not form.is_valid()

    expected = ['This field is required.']
    assert expected == form.errors[field]


def test_password_ditnot_mach(user_form_wrong_password, db):

    form = UserForm(data=user_form_wrong_password)

    assert not form.is_valid()

    expected = ['The two password fields didn’t match.']
    assert expected == form.errors['password2']


@pytest.mark.parametrize(
    'password, error_validation',[
        ( '1', ['This password is too short. It must contain at least 8 characters.',
             'This password is too common.',
             'This password is entirely numeric.']),
        ( '12345678', ['This password is too common.',
                       'This password is entirely numeric.']),
        ( '45268748', ['This password is entirely numeric.']),
    ]
)
def test_password_validation(password, error_validation, db):

    payload = {
        'email': 'test1@email.com',
        'password1': password,
        'password2': password,
    }

    form = UserForm(data=payload)

    assert not form.is_valid()

    assert error_validation == form.errors['password2']
