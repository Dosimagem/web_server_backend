import pytest
from django.utils.translation import gettext as _
from django.utils.translation import ngettext

from web_server.core.serializers import ChangePasswordSerializer


def test_serializer(user, register_infos):

    password = register_infos['password1']

    data = {'old_password': password, 'new_password1': '123455!!', 'new_password2': '123455!!'}

    serializer = ChangePasswordSerializer(data=data, instance=user)

    assert serializer.is_valid()

    data = serializer.validated_data

    assert data['old_password'] == password
    assert data['new_password1'] == '123455!!'
    assert data['new_password2'] == '123455!!'


def test_field_conf():

    serializer = ChangePasswordSerializer()

    assert serializer.fields['old_password'].max_length == 128
    assert serializer.fields['new_password1'].max_length == 128
    assert serializer.fields['new_password2'].max_length == 128


def test_missing_fields():

    serializer = ChangePasswordSerializer(data={})

    assert not serializer.is_valid()

    errors = serializer.errors

    assert errors['old_password'] == ['Este campo é obrigatório.']
    assert errors['new_password1'] == ['Este campo é obrigatório.']
    assert errors['new_password2'] == ['Este campo é obrigatório.']


def test_passwords_dont_mach(user, register_infos):

    password = register_infos['password1']

    data = {'old_password': password, 'new_password1': '12345!!', 'new_password2': '123455!!'}

    serializer = ChangePasswordSerializer(data=data, instance=user)

    assert not serializer.is_valid()

    errors = serializer.errors

    assert errors['new_password2'] == ['Os dois campos da palavra-passe não coincidem.']


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
def test_password_validation(password, error_validation, user, register_infos):

    password_old = register_infos['password1']

    data = {
        'old_password': password_old,
        'new_password1': password,
        'new_password2': password,
    }

    serializer = ChangePasswordSerializer(data=data, instance=user)

    assert not serializer.is_valid()

    assert serializer.errors['non_field_errors'] == error_validation


def test_wrong_old_password(user, register_infos):

    password_old = register_infos['password1']

    data = {
        'old_password': password_old + '11',
        'new_password1': '123456!!',
        'new_password2': '123456!!',
    }

    serializer = ChangePasswordSerializer(data=data, instance=user)

    assert not serializer.is_valid()

    assert serializer.errors['old_password'] == ['Password antigo não está correto.']
