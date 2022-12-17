import pytest

from web_server.conftest import fake
from web_server.core.email import _jwt_verification_email_secret
from web_server.core.serializers import ResetPasswordConfirmSerializer


@pytest.fixture
def data_sent(user):

    token = _jwt_verification_email_secret(user)
    user.reset_password_secret = token
    user.sent_reset_password_email = True
    user.save()

    password = fake.password()

    return {'token': token, 'new_password1': password, 'new_password2': password}


def test_serializer(data_sent):

    serializer = ResetPasswordConfirmSerializer(data=data_sent)

    assert serializer.is_valid()

    assert serializer.validated_data['token'] == data_sent['token']
    assert serializer.validated_data['new_password1'] == data_sent['new_password1']
    assert serializer.validated_data['new_password2'] == data_sent['new_password2']


@pytest.mark.parametrize(
    'field, error',
    [
        ('token', ['Este campo é obrigatório.']),
        ('new_password1', ['Este campo é obrigatório.']),
        ('new_password2', ['Este campo é obrigatório.']),
    ],
)
def test_missing_field(field, error, user, data_sent):

    data_sent.pop(field)

    serializer = ResetPasswordConfirmSerializer(data=data_sent)

    assert not serializer.is_valid()

    assert serializer.errors[field] == error


def test_invalid_field(user):

    password = fake.password()

    data = {'token': 'token', 'new_password1': password, 'new_password2': password + '11'}

    serializer = ResetPasswordConfirmSerializer(data=data)

    assert not serializer.is_valid()

    assert serializer.errors['new_password2'] == ['Os dois campos da palavra-passe não coincidem.']
