from datetime import datetime

import pytest

from web_server.signature.serializers import (
    SignatureCreateSerizaliser,
    SignatureSerializer,
)


@pytest.fixture
def signature_create_data(signature_payload):

    dict_ = signature_payload.copy()
    dict_['trial_time'] = dict_.pop('trialTime')

    return dict_


def test_signature_serializer_with_test_period(user_signature):

    user_signature.test_period_initial = datetime(2001, 1, 2)
    user_signature.test_period_end = datetime(2002, 1, 2)

    serializer = SignatureSerializer(instance=user_signature)

    data = serializer.data

    assert data['uuid'] == str(user_signature.uuid)
    assert data['plan'] == user_signature.plan
    assert data['price'] == user_signature.price
    assert data['hired_period'] is None
    assert data['test_period'] == {
        'initial': user_signature.test_period_initial.strftime('%Y-%m-%d'),
        'end': user_signature.test_period_end.strftime('%Y-%m-%d'),
    }
    assert data['activated'] == user_signature.activated
    assert data['modality'] == user_signature.get_modality_display()
    assert data['discount'] == str(user_signature.discount)
    assert data['bill_url'] is None

    for ser, db in zip(data['benefits'], user_signature.benefits.all()):
        assert ser['uuid'] == str(db.uuid)
        assert ser['name'] == db.name
        assert ser['uri'] == db.uri


def test_signature_serializer_with_hired_period(user_signature):

    user_signature.hired_period_initial = datetime(2001, 1, 2)
    user_signature.hired_period_end = datetime(2002, 1, 2)

    serializer = SignatureSerializer(instance=user_signature)

    data = serializer.data

    assert data['uuid'] == str(user_signature.uuid)
    assert data['plan'] == user_signature.plan
    assert data['price'] == user_signature.price
    assert data['hired_period'] == {
        'initial': user_signature.hired_period_initial.strftime('%Y-%m-%d'),
        'end': user_signature.hired_period_end.strftime('%Y-%m-%d'),
    }
    assert data['test_period'] is None
    assert data['activated'] == user_signature.activated
    assert data['bill_url'] is None
    for ser, db in zip(data['benefits'], user_signature.benefits.all()):
        assert ser['uuid'] == str(db.uuid)
        assert ser['name'] == db.name
        assert ser['uri'] == db.uri


def test_signature_serializer_without_test_or_hired_period(user_signature):

    serializer = SignatureSerializer(instance=user_signature)

    data = serializer.data

    assert data['uuid'] == str(user_signature.uuid)
    assert data['plan'] == user_signature.plan
    assert data['price'] == user_signature.price
    assert data['hired_period'] is None
    assert data['test_period'] is None
    assert data['activated'] == user_signature.activated
    assert data['bill_url'] is None
    for ser, db in zip(data['benefits'], user_signature.benefits.all()):
        assert ser['uuid'] == str(db.uuid)
        assert ser['name'] == db.name
        assert ser['uri'] == db.uri


def test_signature_create_serializer(signature_create_data):
    serializer = SignatureCreateSerizaliser(data=signature_create_data)
    assert serializer.is_valid()


def test_signature_create_serializer_without_discount_and_modality(signature_create_data):
    del signature_create_data['discount']
    del signature_create_data['modality']

    serializer = SignatureCreateSerizaliser(data=signature_create_data)

    assert serializer.is_valid()


def test_positive_signature_create_serializer_save(signature_create_data, user):

    serializer = SignatureCreateSerizaliser(data=signature_create_data)
    assert serializer.is_valid()

    sig = serializer.save(user=user)

    assert sig.pk


def test_positive_signature_create_serializer_trial_time_transform(signature_create_data):
    """
    Must be able to transform '30 day' for 30
    """

    serializer = SignatureCreateSerizaliser(data=signature_create_data)
    assert serializer.is_valid()
    assert serializer.validated_data['trial_time'] == 30


def test_negative_signature_create_serializer_trial_time_not_a_int(signature_create_data):

    signature_create_data['trial_time'] = 'erwer days'

    serializer = SignatureCreateSerizaliser(data=signature_create_data)

    assert not serializer.is_valid()
    assert serializer.errors['trial_time'] == ['Não é um periodo de teste válido. Exemplo: 30 days.']


def test_negative_signature_create_serializer_trial_time_not_in_days(signature_create_data):

    signature_create_data['trial_time'] = '30 year'

    serializer = SignatureCreateSerizaliser(data=signature_create_data)

    assert not serializer.is_valid()
    assert serializer.errors['trial_time'] == ['Não é um periodo de teste válido. Exemplo: 30 days.']


def test_negative_signature_create_serializer_trial_time_wrong_format(signature_create_data):

    signature_create_data['trial_time'] = '30'

    serializer = SignatureCreateSerizaliser(data=signature_create_data)

    assert not serializer.is_valid()
    assert serializer.errors['trial_time'] == ['Não é um periodo de teste válido. Exemplo: 30 days.']


def test_negative_signature_create_serializer_trial_time_negative(signature_create_data):

    signature_create_data['trial_time'] = '-30 days'

    serializer = SignatureCreateSerizaliser(data=signature_create_data)

    assert not serializer.is_valid()
    assert serializer.errors['trial_time'] == ['Não é um periodo de teste válido. Exemplo: 30 days.']


def test_negative_signature_create_serializer_trial_time_wrong_modality(signature_create_data):

    signature_create_data['modality'] = 'wrong'

    serializer = SignatureCreateSerizaliser(data=signature_create_data)

    assert not serializer.is_valid()
    assert serializer.errors['modality'] == ['"wrong" não é uma modalidade válida.']


@pytest.mark.parametrize(
    'field',
    [
        'plan',
        'price',
        'benefits',
        'trial_time',
    ],
)
def test_negative_signature_create_serializer_missing_fields(field, signature_create_data):

    del signature_create_data[field]

    serializer = SignatureCreateSerizaliser(data=signature_create_data)
    assert not serializer.is_valid()
    assert serializer.errors[field] == ['Este campo é obrigatório.']
