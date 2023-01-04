from web_server.core.serializers import PhoneSerializer


def test_serializer(user):

    serializer = PhoneSerializer(data={'phone': '+552228814355'})

    assert serializer.is_valid()

    data = serializer.validated_data

    assert data['phone'] == '+552228814355'


def test_invalid_phone(user):

    serializer = PhoneSerializer(data={'phone': '2228814355'})

    assert not serializer.is_valid()

    assert serializer.errors['phone'] == ['Informe um número de telefone válido.']


def test_missing_fields():

    serializer = PhoneSerializer(data={})

    assert not serializer.is_valid()

    assert serializer.errors['phone'] == ['Este campo é obrigatório.']
