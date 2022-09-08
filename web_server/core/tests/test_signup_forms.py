import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError


from web_server.core.forms import SignupForm
from web_server.core.models import UserProfile


User = get_user_model()


def test_valid_signup_form(register_infos, db):

    form = SignupForm(data=register_infos)

    assert form.is_valid()


@pytest.mark.parametrize(
    'field',
    ['email',
     'confirmed_email',
     'password1',
     'password2',
     'name',
     'phone',
     'clinic',
     'role',
     'cpf',
     'cnpj'],
)
def test_field_is_not_optional(register_infos, field, db):

    del register_infos[field]
    form = SignupForm(data=register_infos)

    assert not form.is_valid()

    expected = ['This field is required.']
    assert expected == form.errors[field]


def test_password_did_not_mach(user_wrong_signup, db):

    form = SignupForm(data=user_wrong_signup)

    assert not form.is_valid()

    expected = ['The two password fields didn’t match.']
    assert expected == form.errors['password2']


def test_email_did_not_mach(user_wrong_signup, db):

    form = SignupForm(data=user_wrong_signup)

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

    form = SignupForm(data=payload)

    assert not form.is_valid()

    assert error_validation == form.errors['password2']


def test_form_clean(db):
    '''
    name: UseR sUname -> User Surname
    phone: +55(11)444020824 -> 551144020824
    institution: any HOSpital -> Any Hospital',
    role: PhysIcian -> physician
    '''
    d = {
        'name': 'UseR sUrname',
        'phone': '+55(11)444020824 ',
        'clinic': 'any HOSpital ',
        'role': 'PhysIcian',
        }

    form = SignupForm(d)
    form.full_clean()

    assert form.cleaned_data['name'] == d['name'].title()
    assert form.cleaned_data['phone'] == '5511444020824'
    assert form.cleaned_data['clinic'] == d['clinic'].strip().title()
    assert form.cleaned_data['role'] == d['role'].lower()


def test_clinic_must_be_unique(user, second_user_login_info, second_user_profile_info):
    second_user_profile_info['clinic'] = user.profile.clinic

    user = User.objects.create_user(**second_user_login_info)

    with pytest.raises(IntegrityError):
        UserProfile.objects.filter(user=user).update(**second_user_profile_info)


def test_save(register_infos, db):

    form = SignupForm(register_infos)
    form.save()

    assert User.objects.exists()
    assert UserProfile.objects.exists()

    user = User.objects.first()

    assert user.email == form.cleaned_data['email']
    assert user.profile.name == form.cleaned_data['name']
    assert user.profile.clinic == form.cleaned_data['clinic']
    assert user.profile.role == form.cleaned_data['role']
    assert user.profile.phone == form.cleaned_data['phone']
    assert user.profile.cpf == form.cleaned_data['cpf']
    assert user.profile.cnpj == form.cleaned_data['cnpj']
