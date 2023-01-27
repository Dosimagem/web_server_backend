import pytest
from django.contrib.auth import get_user_model

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


def test_only_check_the_uniqueness_of_the_cpf_if_it_is_not_empty(user_info, second_user_login_info, register_infos, db):

    del register_infos['cnpj']
    del register_infos['cpf']

    user = User.objects.create_user(**user_info)
    profile_infos = register_infos
    profile_infos['user'] = user

    form = ProfileCreateForm(data=profile_infos, instance=profile_infos['user'].profile)

    assert form.is_valid()

    form.save()

    user = User.objects.create_user(**second_user_login_info)
    profile_infos = register_infos
    profile_infos['user'] = user

    form = ProfileCreateForm(data=profile_infos, instance=user)
    assert form.is_valid()


def test_valid_form_without_cpf_and_cnpf(register_infos_without_cpf_and_cnpj, user_info, db):

    user = User.objects.create_user(**user_info)
    profile_infos = register_infos_without_cpf_and_cnpj
    profile_infos['user'] = user

    form = ProfileCreateForm(data=profile_infos, instance=profile_infos['user'].profile)

    assert form.is_valid()


# def test_cnpj_missing(profile_infos):

#     profile_infos.pop('cnpj')
#     form = ProfileCreateForm(data=profile_infos, instance=profile_infos['user'].profile)

#     assert not form.is_valid()

#     expected = ['Este campo é obrigatório.']
#     assert form.errors['cnpj'] == expected


@pytest.mark.parametrize(
    'field',
    [
        'user',
        'name',
        'phone',
        'clinic',
        'role',
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

    expected = ['Este campo é obrigatório.']
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

    assert form.errors['cpf'] == ['CPF já existe']


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

    assert form.errors['cpf'] == ['CPF inválido.']


def test_cnpj_invalid(second_register_infos, db):

    second_register_infos['cnpj'] = 1

    form = ProfileCreateForm(second_register_infos)

    assert not form.is_valid()

    assert form.errors['cnpj'] == ['CNPJ inválido.']


def test_phone_invalid(db):

    form = ProfileCreateForm({'phone': '222222222'})

    assert not form.is_valid()

    expected = ['Introduza um número de telefone válido (ex. +12125552368).']

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
    assert user.profile.phone_str == form.cleaned_data['phone']
    assert user.profile.cpf == form.cleaned_data['cpf']
    assert user.profile.cnpj == form.cleaned_data['cnpj']


def test_update_profile_form_succesuful(api_cnpj_successfull, user):

    payload = {
        'name': 'João Silva Carvalho',
        'role': 'médico',
        'cnpj': '42438610000111',
        'clinic': 'Clinica A',
    }

    form = ProfileUpdateForm(data=payload, instance=user.profile)

    assert form.is_valid()

    form.save()

    user_db = User.objects.first()

    assert user_db.profile.name == 'João Silva Carvalho'


def test_fail_name_must_have_not_numbers(api_cnpj_successfull, profile_infos):

    profile_infos['name'] = 'User 1'

    form = ProfileCreateForm(data=profile_infos, instance=profile_infos['user'].profile)

    assert not form.is_valid()

    expected = {'name': ['O nome não pode ter números.']}

    assert expected == form.errors


def test_fail_name_can_not_have_numbers(api_cnpj_successfull, profile_infos):

    profile_infos['name'] = 'User 1'

    form = ProfileCreateForm(data=profile_infos, instance=profile_infos['user'].profile)

    assert not form.is_valid()

    expected = {'name': ['O nome não pode ter números.']}

    assert expected == form.errors


def test_fail_name_length_must_least_3(api_cnpj_successfull, profile_infos):

    profile_infos['name'] = 'ii'

    form = ProfileCreateForm(data=profile_infos, instance=profile_infos['user'].profile)

    assert not form.is_valid()

    expected = ['Certifique-se de que o valor tenha no mínimo 3 caracteres (ele possui 2).']

    assert {'name': expected} == form.errors


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
