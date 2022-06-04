from web_server.users.forms import SignUpForm


def test_valid_form(user_form):
    form = SignUpForm(data=user_form)

    assert form.is_valid()


def test_password_ditnot_mach(user_form_wrong_password):

    form = SignUpForm(data=user_form_wrong_password)

    assert not form.is_valid()

    expected = ['The two password fields didn’t match.']
    assert expected == form.errors['password2']
