import pytest
from django.contrib.auth import get_user_model
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

    expected = ['Este campo é obrigatório.']
    assert expected == form.errors[field]


def test_password_did_not_mach(register_infos, db):

    register_infos['password2'] = register_infos['password2'] + '!'

    form = MyUserCreationForm(data=register_infos)

    assert not form.is_valid()

    expected = ['Os dois campos de senha não correspondem.']
    assert expected == form.errors['password2']


def test_email_did_not_mach(register_infos, db):

    register_infos['confirmed_email'] = 'a' + register_infos['confirmed_email']

    form = MyUserCreationForm(data=register_infos)

    assert not form.is_valid()

    expected = ['Os dois campos de e-mail não correspondem.']
    assert expected == form.errors['confirmed_email']


@pytest.mark.parametrize(
    'password, error_validation',
    [
        (
            '1',
            [
                'Esta senha é muito curta. Ela precisa conter pelo menos 8 caracteres.',
                'Esta senha é muito comum.',
                'Esta senha é inteiramente numérica.',
            ],
        ),
        (
            '12345678',
            [
                'Esta senha é muito comum.',
                'Esta senha é inteiramente numérica.',
            ],
        ),
        ('45268748', ['Esta senha é inteiramente numérica.']),
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
