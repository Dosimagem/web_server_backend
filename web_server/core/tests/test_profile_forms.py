import pytest
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _

from web_server.core.forms import ProfileCreateForm, ProfileUpdateForm
from web_server.core.models import UserProfile

User = get_user_model()


@pytest.fixture
def profile_infos(register_infos, user_info, db):

    user = User.objects.create_user(**user_info)
    profile_infos = register_infos
    profile_infos['user'] = user

    return profile_infos


def test_valid_form(api_cnpj_successfull, profile_infos):

    form = ProfileCreateForm(data=profile_infos, instance=profile_infos['user'].profile)

    assert form.is_valid()


def test_cnpj_missing(profile_infos):

    profile_infos.pop('cnpj')
    form = ProfileCreateForm(data=profile_infos, instance=profile_infos['user'].profile)

    assert not form.is_valid()

    expected = [_('This field is required.')]
    assert form.errors['cnpj'] == expected


@pytest.mark.parametrize(
    'field',
    [
        'user',
        'name',
        'phone',
        'clinic',
        'role',
        'cpf',
    ],
)
def test_field_missing(api_cnpj_successfull, profile_infos, field):

    if field == 'user':
        user = profile_infos.pop(field)
        form = ProfileCreateForm(data=profile_infos, instance=user.profile)
    else:
        profile_infos.pop(field)
        form = ProfileCreateForm(data=profile_infos, instance=profile_infos['user'].profile)

    assert not form.is_valid()

    expected = [_('This field is required.')]
    assert form.errors[field] == expected


def test_form_clean(db):
    """
    name: UseR sUname -> User Surname
    institution: any HOSpital -> Any Hospital',
    role: PhysIcian -> physician
    """
    d = {
        'name': 'UseR sUrname',
        'clinic': 'any HOSpital ',
        'role': 'PhysIcian',
    }

    form = ProfileCreateForm(d)
    form.full_clean()

    assert form.cleaned_data['name'] == d['name'].title()
    assert form.cleaned_data['clinic'] == d['clinic'].strip().title()
    assert form.cleaned_data['role'] == d['role'].lower()


# TODO: Should the Clinic name be unique?
# def test_clinic_must_be_unique(api_cnpj_fail, user, second_register_infos):

#     second_register_infos['clinic'] = user.profile.clinic

#     form = ProfileCreateForm(second_register_infos)

#     assert not form.is_valid()

#     assert form.errors['clinic'] == ['Clinic already exists']


def test_cpf_must_be_unique(api_cnpj_fail, user, second_register_infos):
    second_register_infos['cpf'] = user.profile.cpf

    form = ProfileCreateForm(second_register_infos)

    assert not form.is_valid()

    assert form.errors['cpf'] == ['CPF already exists']


# TODO: Should the CNPJ be unique ?
# def test_cnpj_must_be_unique(user, second_register_infos, db):
#     second_register_infos['cnpj'] = user.profile.cnpj

#     form = ProfileCreateForm(second_register_infos)

#     assert not form.is_valid()

#     assert form.errors['cnpj'] == ['CNPJ already exists']


def test_cpf_invalid(api_cnpj_fail, second_register_infos, db):

    second_register_infos['cpf'] = 1

    form = ProfileCreateForm(second_register_infos)

    assert not form.is_valid()

    assert form.errors['cpf'] == ['CPF invalid.']


def test_cnpj_invalid(second_register_infos, db):

    second_register_infos['cnpj'] = 1

    form = ProfileCreateForm(second_register_infos)

    assert not form.is_valid()

    assert form.errors['cnpj'] == ['CNPJ invalid.']


def test_phone_invalid():

    form = ProfileCreateForm({'phone': '22222-2222'})

    assert not form.is_valid()

    expected = ['Número de telefone inválido. O formato deve ser xx(xx)xxxx-xxxx ou xx(xx)xxxxx-xxxx.']

    assert form.errors['phone'] == expected


def test_cnpj_api_invalid(api_cnpj_fail, second_register_infos, db):

    form = ProfileCreateForm(second_register_infos)

    assert not form.is_valid()

    assert form.errors['cnpj'] == ['CNPJ 83.398.534/0001-45 não encontrado.']


def test_create_save(api_cnpj_successfull, profile_infos):

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


def test_update_profile_form_succesuful(api_cnpj_successfull, user):

    payload = {
        'name': 'João Sliva Carvalho',
        'role': 'médico',
        'cnpj': '42438610000111',
        'clinic': 'Clinica A',
    }

    assert user.profile.name == 'João Silva'

    form = ProfileUpdateForm(data=payload, instance=user.profile)

    assert form.is_valid()

    form.save()

    user_db = User.objects.first()

    assert user_db.profile.name == 'João Sliva Carvalho'


# def test_fail_update_profile_form_clinic_unique_constraint(api_cnpj_successfull, user, second_user):

#     payload = {
#         'name': 'João Sliva Carvalho',
#         'role': 'médico',
#         'cnpj': '42438610000111',
#         'clinic': second_user.profile.clinic
#     }

#     form = ProfileUpdateForm(data=payload, instance=user.profile)

#     assert not form.is_valid()

#     assert form.errors['clinic'] == ['Clinic already exists']


# def test_fail_update_profile_form_cnpj_unique_constraint(user, second_user):

#     payload = {
#         'name': 'João Sliva Carvalho',
#         'role': 'médico',
#         'cnpj': second_user.profile.cnpj,
#         'clinic': 'Clinica A'
#     }

#     form = ProfileUpdateForm(data=payload, instance=user.profile)

#     assert not form.is_valid()

#     assert form.errors['cnpj'] == ['CNPJ already exists']
