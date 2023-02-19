from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.shortcuts import resolve_url

User = get_user_model()


END_POINT = 'signatures:signature-list-create'


# /api/v1/users/<uuid>/signatures/ - GET


def test_successfull(client_api_auth, user, user_signature, user_other_signature):

    url = resolve_url(END_POINT, user.uuid)

    resp = client_api_auth.get(url)
    body = resp.json()

    signature_db = user.signatures.filter(user=user)

    assert resp.status_code == HTTPStatus.OK

    assert 2 == body['count']

    for expected, body_response in zip(signature_db, body['row']):
        assert body_response['plan'] == expected.plan
        assert body_response['uuid'] == str(expected.uuid)
        assert body_response['hiredPeriod'] == expected.hired_period
        assert body_response['testPeriod'] == expected.test_period
        assert body_response['price'] == str(expected.price)
        assert body_response['activated'] == expected.activated
        assert body_response['modality'] == expected.get_modality_display()
        assert body_response['discount'] == str(expected.discount)


        for e_db, e_resp in zip(expected.benefits.all(), body_response['benefits']):
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
