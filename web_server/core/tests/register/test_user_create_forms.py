import pytest
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _
from django.utils.translation import ngettext

from web_server.core.forms import MyUserCreationForm
from web_server.core.models import UserProfile

User = get_user_model()


def test_valid_form(register_infos, db):

    form = MyUserCreationForm(data=register_infos)

    assert form.is_valid()


@pytest.mark.parametrize(
    'field',
    [
        'email',
        'confirmed_email',
        'password1',
        'password2',
    ],
)
def test_field_is_not_optional(register_infos, field, db):

    del register_infos[field]
    form = MyUserCreationForm(data=register_infos)

    assert not form.is_valid()

    expected = [_('This field is required.')]
    assert expected == form.errors[field]


def test_password_did_not_mach(register_infos, db):

    register_infos['password2'] = register_infos['password2'] + '!'

    form = MyUserCreationForm(data=register_infos)

    assert not form.is_valid()

    expected = [_('The two password fields didn’t match.')]
    assert expected == form.errors['password2']


def test_email_did_not_mach(register_infos, db):

    register_infos['confirmed_email'] = 'a' + register_infos['confirmed_email']

    form = MyUserCreationForm(data=register_infos)

    assert not form.is_valid()

    expected = ['Os campos emails não correspondem.']
    assert expected == form.errors['confirmed_email']


MSG_PASSWORD = ngettext(
    'This password is too short. It must contain at least %(min_length)d character.',
    'This password is too short. It must contain at least %(min_length)d characters.',
    8,
) % {'min_length': 8}


@pytest.mark.parametrize(
    'password, error_validation',
    [
        (
            '1',
            [
                MSG_PASSWORD,
                _('This password is too common.'),
                _('This password is entirely numeric.'),
            ],
        ),
        (
            '12345678',
            [
                _('This password is too common.'),
                _('This password is entirely numeric.'),
            ],
        ),
        ('45268748', [_('This password is entirely numeric.')]),
    ],
)
def test_password_validation(password, error_validation, db):

    payload = {
        'email': 'test1@email.com',
        'password1': password,
        'password2': password,
    }

    form = MyUserCreationForm(data=payload)

    assert not form.is_valid()

    assert error_validation == form.errors['password2']


def test_save(register_infos, db):

    form = MyUserCreationForm(register_infos)
    form.full_clean()
    form.save()

    assert User.objects.exists()
    assert UserProfile.objects.exists()

    user = User.objects.first()

    assert user.email == form.cleaned_data['email']
    assert user.profile.name == ''
    assert user.profile.clinic == ''
    assert user.profile.role == ''
    assert user.profile.phone_str == ''
    assert user.profile.cpf == ''
    assert user.profile.cnpj == ''
