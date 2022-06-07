import pytest
from web_server.users.forms import SignUpForm


def test_valid_form(user_form):

    form = SignUpForm(data=user_form)

    assert form.is_valid()


@pytest.mark.parametrize(
    'field',
    ['email', 'phone', 'institution', 'role'],
)
def test_field_isnot_optional(user_form, field):

    del user_form[field]
    form = SignUpForm(data=user_form)

    assert not form.is_valid()

    expected = ['This field is required.']
    assert expected == form.errors[field]


def test_username_is_optional(user_form):

    del user_form['name']
    form = SignUpForm(data=user_form)

    assert form.is_valid()


def test_password_ditnot_mach(user_form_wrong_password):

    form = SignUpForm(data=user_form_wrong_password)

    assert not form.is_valid()

    expected = ['The two password fields didn’t match.']
    assert expected == form.errors['password2']
