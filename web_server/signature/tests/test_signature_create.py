from http import HTTPStatus

import pytest
from django.core import mail
from django.shortcuts import resolve_url

from web_server.core.email import DOSIMAGEM_EMAIL
from web_server.signature.models import Signature

END_POINT = 'signatures:signature-list-create'


# /api/v1/users/<uuid>/signatures/ - POST


def test_successfull(client_api_auth, user, signature_payload):

    url = resolve_url(END_POINT, user.uuid)

    resp = client_api_auth.post(url, data=signature_payload, format='json')

    assert resp.status_code == HTTPStatus.CREATED

    body = resp.json()

    signature = Signature.objects.get(user=user, plan=signature_payload['plan'])
    benefit_list = signature.benefits.all()

    assert signature_payload['plan'] == signature.plan
    assert signature_payload['price'] == str(signature.price)
    for ben_payload, ben_db in zip(signature_payload['benefits'], benefit_list):
        assert ben_payload == ben_db.name

    assert body['plan'] == signature.plan
    assert body['hiredPeriod'] is None
    assert body['testPeriod']['end'] == str(signature.test_period['end'])
    assert body['testPeriod']['initial'] == str(signature.test_period['initial'])
    assert body['price'] == str(signature.price)
    assert body['activated'] == signature.activated
    assert body['modality'] == signature.get_modality_display()
    assert body['discount'] == str(signature.discount)

    for ben_db, ben_resp in zip(benefit_list, body['benefits']):
        assert str(ben_db.uuid) == ben_resp['uuid']
        assert ben_db.name == ben_resp['name']
        assert ben_db.uri == ben_resp['uri']

    email = mail.outbox[0]

    assert 'Nova assinatura' == email.subject
    assert DOSIMAGEM_EMAIL == email.from_email
    assert [DOSIMAGEM_EMAIL] == email.to

    assert signature_payload['plan'] in email.body
    assert signature_payload['price'] in email.body
    assert signature_payload['discount'] in email.body
    for ben in signature_payload['benefits']:
        assert ben in email.body


def test_negative_user_can_only_one_signature_per_plan(client_api_auth, user, signature_payload):

    url = resolve_url(END_POINT, user.uuid)

    resp = client_api_auth.post(url, data=signature_payload, format='json')

    assert resp.status_code == HTTPStatus.CREATED

    resp = client_api_auth.post(url, data=signature_payload, format='json')

    assert resp.status_code == HTTPStatus.CONFLICT

    body = resp.json()

    assert body['errors'] == ['O usuário já assinou esse plano.']

    assert Signature.objects.count() == 1


def test_negative_not_register_benfits(client_api_auth, user, signature_payload):
    """
    The benefits A2 is not register.
    """

    signature_payload['benefits'] = ['B1', 'A2']

    url = resolve_url(END_POINT, user.uuid)

    resp = client_api_auth.post(url, data=signature_payload, format='json')

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    body = resp.json()

    assert not Signature.objects.exists()

    assert body['errors'] == ['benefits: The benefit A2 is not registered.']


@pytest.mark.parametrize(
    'field, error',
    [
        ('plan', ['plan: Este campo é obrigatório.']),
        ('price', ['price: Este campo é obrigatório.']),
        ('benefits', ['benefits: Este campo é obrigatório.']),
        ('trialTime', ['trial_time: Este campo é obrigatório.']),
    ],
)
def test_negative_missing_fields(client_api_auth, field, error, user, signature_payload):

    del signature_payload[field]

    url = resolve_url(END_POINT, user.uuid)

    resp = client_api_auth.post(url, data=signature_payload, format='json')

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    body = resp.json()

    assert body['errors'] == error


def test_negative_trial_time_not_a_int(client_api_auth, user, signature_payload):

    signature_payload['trialTime'] = 'erwer days'

    url = resolve_url(END_POINT, user.uuid)

    resp = client_api_auth.post(url, data=signature_payload, format='json')

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    body = resp.json()

    assert body['errors'] == ['trial_time: Não é um periodo de teste válido. Exemplo: 30 days.']


def test_negative_trial_time_not_in_days(client_api_auth, user, signature_payload):

    signature_payload['trialTime'] = '30 years'

    url = resolve_url(END_POINT, user.uuid)

    resp = client_api_auth.post(url, data=signature_payload, format='json')

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    body = resp.json()

    assert body['errors'] == ['trial_time: Não é um periodo de teste válido. Exemplo: 30 days.']


def test_negative_trial_time_negative(client_api_auth, user, signature_payload):

    signature_payload['trialTime'] = '-30 days'

    url = resolve_url(END_POINT, user.uuid)

    resp = client_api_auth.post(url, data=signature_payload, format='json')

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    body = resp.json()

    assert body['errors'] == ['trial_time: Não é um periodo de teste válido. Exemplo: 30 days.']
