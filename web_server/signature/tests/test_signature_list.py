from http import HTTPStatus

import pytest
from dj_rest_auth.utils import jwt_encode
from django.contrib.auth import get_user_model
from django.shortcuts import resolve_url
from freezegun import freeze_time

from web_server.signature.models import Signature
from web_server.signature.tests.constants import (
    DATE_END_1,
    DATE_END_2,
    DATE_START_1,
    DATE_START_2,
)

User = get_user_model()


END_POINT = 'signatures:signature-list-create'


# /api/v1/users/<uuid>/signatures/ - GET


@pytest.fixture
@freeze_time('2022-05-02 00:00:00')
def client_api_auth_fix_time(client_api, user):
    access_token, _ = jwt_encode(user)
    client_api.cookies.load({'jwt-access-token': access_token})
    return client_api


@pytest.fixture
def signature_list(user, benefit_list):

    sig1_yet_valid = Signature.objects.create(
        user=user,
        plan='Pacote 1',
        price='600.00',
        test_period_initial=DATE_START_2,
        test_period_end=DATE_END_2,
        bill='bill.pdf',
    )
    sig1_yet_valid.benefits.add(*benefit_list)

    sig2 = Signature.objects.create(
        user=user,
        plan='Pacote 2',
        price='700.00',
        test_period_initial=DATE_START_1,
        test_period_end=DATE_END_1,
    )
    sig2.benefits.add(benefit_list[2])

    sig3_yet_valid = Signature.objects.create(
        user=user,
        plan='Pacote 3',
        price='200.00',
        hired_period_initial=DATE_START_2,
        hired_period_end=DATE_END_2,
    )
    sig3_yet_valid.benefits.add(benefit_list[1])

    _ = Signature.objects.create(user=user, plan='Pacote 4', price='60.00')

    return [sig1_yet_valid, sig3_yet_valid]


@freeze_time('2022-05-02 00:00:00')
def test_successfull(client_api_auth_fix_time, user, signature_list):
    """
    Must list only signatures in valid period
    """

    url = resolve_url(END_POINT, user.uuid)

    resp = client_api_auth_fix_time.get(url)
    body = resp.json()

    assert resp.status_code == HTTPStatus.OK

    assert 2 == body['count']

    for from_db, body_response in zip(signature_list, body['row']):
        assert body_response['plan'] == from_db.plan
        assert body_response['uuid'] == str(from_db.uuid)
        assert body_response['hiredPeriod'] == from_db.hired_period
        assert body_response['testPeriod'] == from_db.test_period
        assert body_response['price'] == str(from_db.price)
        assert body_response['activated'] == from_db.activated
        assert body_response['modality'] == from_db.get_modality_display()
        assert body_response['discount'] == str(from_db.discount)
        assert body_response['statusPayment'] == 'Aguardando pagamento'
        if from_db.bill.name:
            assert body_response['billUrl'] == 'http://testserver/media/bill.pdf'
        else:
            assert body_response['billUrl'] is None

        for e_db, e_resp in zip(from_db.benefits.all(), body_response['benefits']):
            assert e_resp['uuid'] == str(e_db.uuid)
            assert e_resp['name'] == e_db.name
            assert e_resp['uri'] == e_db.uri

        # TODO: colocar a data de criação e update


def test_user_not_have_signatures(client_api_auth, user):

    url = resolve_url(END_POINT, user.uuid)

    resp = client_api_auth.get(url)

    assert resp.status_code == HTTPStatus.OK

    body = resp.json()

    assert body['count'] == 0
    assert body['row'] == []
