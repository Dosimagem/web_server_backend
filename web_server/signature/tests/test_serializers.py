from datetime import datetime

from web_server.signature.serializers import (
    BenefitSerializer,
    SignatureByUserSerializer,
)


def test_benefit_serializer(benefit):

    serializer = BenefitSerializer(instance=benefit)

    data = serializer.data

    assert data['uuid'] == str(benefit.uuid)
    assert data['name'] == 'RSV'
    assert data['uri'] == '/dashboard/my-signatures/Benefit/calculator'


def test_signature_serializer_with_test_period(user_signature):

    user_signature.test_period_initial = datetime(2001, 1, 2)
    user_signature.test_period_end = datetime(2002, 1, 2)

    serializer = SignatureByUserSerializer(instance=user_signature)

    data = serializer.data

    assert data['uuid'] == str(user_signature.uuid)
    assert data['name'] == user_signature.name
    assert data['price'] == user_signature.price
    assert data['hired_period'] is None
    assert data['test_period'] == {'initial': user_signature.test_period_initial, 'end': user_signature.test_period_end}
    assert data['activated'] == user_signature.activated

    for ser, db in zip(data['benefits'], user_signature.benefits.all()):
        assert ser['uuid'] == str(db.uuid)
        assert ser['name'] == db.name
        assert ser['uri'] == db.uri


def test_signature_serializer_with_hired_period(user_signature):

    user_signature.hired_period_initial = datetime(2001, 1, 2)
    user_signature.hired_period_end = datetime(2002, 1, 2)

    serializer = SignatureByUserSerializer(instance=user_signature)

    data = serializer.data

    assert data['uuid'] == str(user_signature.uuid)
    assert data['name'] == user_signature.name
    assert data['price'] == user_signature.price
    assert data['hired_period'] == {
        'initial': user_signature.hired_period_initial,
        'end': user_signature.hired_period_end,
    }
    assert data['test_period'] is None
    assert data['activated'] == user_signature.activated
    for ser, db in zip(data['benefits'], user_signature.benefits.all()):
        assert ser['uuid'] == str(db.uuid)
        assert ser['name'] == db.name
        assert ser['uri'] == db.uri


def test_signature_serializer_without_test_or_hired_period(user_signature):

    serializer = SignatureByUserSerializer(instance=user_signature)

    data = serializer.data

    assert data['uuid'] == str(user_signature.uuid)
    assert data['name'] == user_signature.name
    assert data['price'] == user_signature.price
    assert data['hired_period'] is None
    assert data['test_period'] is None
    assert data['activated'] == user_signature.activated
    for ser, db in zip(data['benefits'], user_signature.benefits.all()):
        assert ser['uuid'] == str(db.uuid)
        assert ser['name'] == db.name
        assert ser['uri'] == db.uri
