import pytest

from web_server.contact.serializers import ContactSerializer


def test_positive_serializer(contact_data):

    serializer = ContactSerializer(data=contact_data)
    assert serializer.is_valid()


@pytest.mark.parametrize(
    'field',
    [
        'full_name',
        'email',
        'role',
        'clinic',
        'phone',
        'subject',
        'message',
    ],
)
def test_negative_missing_fields(field, contact_data):

    del contact_data[field]

    serializer = ContactSerializer(data=contact_data)

    assert not serializer.is_valid()

    assert serializer.errors[field] == ['Este campo é obrigatório.']


def test_negative_phone_number(contact_data):

    contact_data['phone'] = '11'

    serializer = ContactSerializer(data=contact_data)

    assert not serializer.is_valid()

    assert serializer.errors['phone'] == ['Informe um número de telefone válido.']
