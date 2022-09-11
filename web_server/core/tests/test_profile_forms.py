import pytest
from django.contrib.auth import get_user_model

from web_server.core.forms import ProfileCreateForm
from web_server.core.models import UserProfile


User = get_user_model()


@pytest.fixture
def profile_infos(register_infos, user_info, db):

    user = User.objects.create_user(**user_info)
    profile_infos = register_infos
    profile_infos['user'] = user

    return profile_infos


def test_valid_form(profile_infos):

    form = ProfileCreateForm(data=profile_infos, instance=profile_infos['user'].profile)

    assert form.is_valid()


@pytest.mark.parametrize(
    'field',
    [
     'user',
     'name',
     'phone',
     'clinic',
     'role',
     'cpf',
     'cnpj'],
)
def test_field_missing(profile_infos, field):

    if field == 'user':
        user = profile_infos.pop(field)
        form = ProfileCreateForm(data=profile_infos, instance=user.profile)
    else:
        profile_infos.pop(field)
        form = ProfileCreateForm(data=profile_infos, instance=profile_infos['user'].profile)

    assert not form.is_valid()

    expected = ['This field is required.']
    assert expected == form.errors[field]


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

    form = ProfileCreateForm(d)
    form.full_clean()

    assert form.cleaned_data['name'] == d['name'].title()
    assert form.cleaned_data['phone'] == '5511444020824'
    assert form.cleaned_data['clinic'] == d['clinic'].strip().title()
    assert form.cleaned_data['role'] == d['role'].lower()


def test_clinic_must_be_unique(user, second_register_infos):

    second_register_infos['clinic'] = user.profile.clinic

    form = ProfileCreateForm(second_register_infos)

    assert not form.is_valid()

    assert form.errors['clinic'] == ['Clinic already exists']


def test_cpf_must_be_unique(user, second_register_infos):
    second_register_infos['cpf'] = user.profile.cpf

    form = ProfileCreateForm(second_register_infos)

    assert not form.is_valid()

    assert form.errors['cpf'] == ['CPF already exists']


def test_cnpj_must_be_unique(user, second_register_infos, db):
    second_register_infos['cnpj'] = user.profile.cnpj

    form = ProfileCreateForm(second_register_infos)

    assert not form.is_valid()

    assert form.errors['cnpj'] == ['CNPJ already exists']


def test_cpf_invalid(second_register_infos, db):

    second_register_infos['cpf'] = 1

    form = ProfileCreateForm(second_register_infos)

    assert not form.is_valid()

    assert form.errors['cpf'] == ['CPF invalid.']


def test_cnpf_invalid(second_register_infos, db):

    second_register_infos['cnpj'] = 1

    form = ProfileCreateForm(second_register_infos)

    assert not form.is_valid()

    assert form.errors['cnpj'] == ['CNPJ invalid.']


def test_save(profile_infos):

    form = ProfileCreateForm(profile_infos, instance=profile_infos['user'].profile)

    assert form.is_valid()

    form.save()

    assert UserProfile.objects.exists()

    user = User.objects.first()

    assert user.profile.name == form.cleaned_data['name']
    assert user.profile.clinic == form.cleaned_data['clinic']
    assert user.profile.role == form.cleaned_data['role']
    assert user.profile.phone == form.cleaned_data['phone']
    assert user.profile.cpf == form.cleaned_data['cpf']
    assert user.profile.cnpj == form.cleaned_data['cnpj']
