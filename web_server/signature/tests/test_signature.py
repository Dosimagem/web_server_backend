from http import HTTPStatus

from django.shortcuts import resolve_url

from web_server.core.errors_msg import MSG_ERROR_TOKEN_USER
from web_server.signature.models import Signature


END_POINT = 'signatures:signature-list-create'


# /api/v1/users/<uuid>/signatures/ - POST

def test_successfull(client_api_auth, user, signature_payload):

    url = resolve_url(END_POINT, user.uuid)

    resp = client_api_auth.post(url, data=signature_payload, format='json')

    assert resp.status_code == HTTPStatus.CREATED

    body = resp.json()

    signature = Signature.objects.get(user=user, name=signature_payload["plan"])
    benefit_list = signature.benefits.all()

    assert signature_payload["plan"] == signature.name
    assert signature_payload["price"] == str(signature.price)
    for ben_payload, ben_db in zip(signature_payload["benefits"], benefit_list):
        assert ben_payload == ben_db.name

    assert body['name'] == signature.name
    assert body['hiredPeriod'] is None
    assert body['testPeriod']['end'] == str(signature.test_period['end'])
    assert body['testPeriod']['initial'] == str(signature.test_period['initial'])
    assert body['price'] ==  str(signature.price)
    assert body['activated'] == signature.activated

    for ben_db, ben_resp in zip(benefit_list, body['benefits']):
        assert str(ben_db.uuid) == ben_resp['uuid']
        assert ben_db.name == ben_resp['name']
        assert ben_db.uri == ben_resp['uri']
