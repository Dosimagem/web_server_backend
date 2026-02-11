import pytest

from web_server.contact.serializers import ContactSerializer


def test_positive_serializer(contact_data):

    serializer = ContactSerializer(data=contact_data)
    assert serializer.is_valid()


@pytest.mark.parametrize(
    'field',
    [
        'name',
        'email',
        'role',
        'company',
        'number',
        'subject',
        'message',
    ],
)
def test_negative_missing_fields(field, contact_data):

    del contact_data[field]

    serializer = ContactSerializer(data=contact_data)

    assert not serializer.is_valid()

    assert serializer.errors[field] == ['Este campo é obrigatório.']
