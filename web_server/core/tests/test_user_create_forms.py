import pytest
from django.contrib.auth import get_user_model

from web_server.core.forms import UserCreationForm
from web_server.core.models import UserProfile


User = get_user_model()


def test_valid_form(register_infos, db):

    form = UserCreationForm(data=register_infos)

    assert form.is_valid()


@pytest.mark.parametrize(
    'field',
    ['email',
     'confirmed_email',
     'password1',
     'password2',
     ],
)
def test_field_is_not_optional(register_infos, field, db):

    del register_infos[field]
    form = UserCreationForm(data=register_infos)

    assert not form.is_valid()

    expected = ['This field is required.']
    assert expected == form.errors[field]


def test_password_did_not_mach(user_wrong_signup, db):

    form = UserCreationForm(data=user_wrong_signup)

    assert not form.is_valid()

    expected = ['The two password fields didn’t match.']
    assert expected == form.errors['password2']


def test_email_did_not_mach(user_wrong_signup, db):

    form = UserCreationForm(data=user_wrong_signup)

    assert not form.is_valid()

    expected = ['The two email fields didn’t match.']
    assert expected == form.errors['confirmed_email']


@pytest.mark.parametrize(
    'password, error_validation', [
        ('1', ['This password is too short. It must contain at least 8 characters.',
               'This password is too common.',
               'This password is entirely numeric.']),
        ('12345678', ['This password is too common.',
                      'This password is entirely numeric.']),
        ('45268748', ['This password is entirely numeric.']),
    ]
)
def test_password_validation(password, error_validation, db):

    payload = {
        'email': 'test1@email.com',
        'password1': password,
        'password2': password,
    }

    form = UserCreationForm(data=payload)

    assert not form.is_valid()

    assert error_validation == form.errors['password2']


def test_save(register_infos, db):

    form = UserCreationForm(register_infos)
    form.save()

    assert User.objects.exists()
    assert UserProfile.objects.exists()

    user = User.objects.first()

    assert user.email == form.cleaned_data['email']
    assert user.profile.name == ''
    assert user.profile.clinic == ''
    assert user.profile.role == ''
    assert user.profile.phone == ''
    assert user.profile.cpf == ''
    assert user.profile.cnpj == ''