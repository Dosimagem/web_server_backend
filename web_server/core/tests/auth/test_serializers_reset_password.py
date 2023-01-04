from web_server.core.serializers import ResetPasswordSerializer


def test_serializer(user):

    data = {'email': user.email}

    serializer = ResetPasswordSerializer(data=data)

    assert serializer.is_valid()

    assert serializer.validated_data['email'] == user.email


def test_missing_field():

    serializer = ResetPasswordSerializer(data={})

    assert not serializer.is_valid()

    assert serializer.errors['email'] == ['Este campo é obrigatório.']


def test_invalid_field():

    serializer = ResetPasswordSerializer(data={'email': 'usermail.com'})

    assert not serializer.is_valid()

    assert serializer.errors['email'] == ['Insira um endereço de email válido.']
