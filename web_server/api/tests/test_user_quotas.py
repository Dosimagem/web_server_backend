from decimal import Decimal
from http import HTTPStatus
from uuid import uuid4

import pytest
from django.shortcuts import resolve_url

from web_server.service.models import UserQuota


@pytest.fixture
def client_api_auth(client_api, user):
    client_api.credentials(HTTP_AUTHORIZATION='Bearer ' + user.auth_token.key)
    return client_api


@pytest.fixture
def url(user):
    return resolve_url('api:quotas', user.uuid)


def test_create_quotas_successfully_with(client_api_auth, create_quota_data, url):
    '''
    endpoint: /api/v1/users/<uuid>/quotas/ - POST
    '''

    response = client_api_auth.post(url, data=create_quota_data)

    assert response.status_code == HTTPStatus.CREATED

    body = response.json()

    assert body['amount'] == create_quota_data['amount']
    assert Decimal(body['price']) == Decimal(create_quota_data['price'])
    assert body['service_type'] == 'Dosimetria Clinica'
    assert body['status_payment'] == 'Aguardando pagamento'
    assert 'created_at' in body

    assert UserQuota.objects.exists()

    quota_db = UserQuota.objects.first()

    assert quota_db.amount == create_quota_data['amount']
    assert quota_db.price == Decimal(create_quota_data['price'])
    assert quota_db.service_type == UserQuota.DOSIMETRY_CLINIC
    assert quota_db.status_payment == UserQuota.AWAITING_PAYMENT


def test_create_quotas_invalid_amount_negative(client_api_auth, create_quota_data, url):
    '''
    endpoint: /api/v1/users/<uuid>/quotas/ - POST
    '''

    create_quota_data['amount'] = -10

    response = client_api_auth.post(url, data=create_quota_data)

    assert response.status_code == HTTPStatus.BAD_REQUEST

    body = response.json()

    assert body['errors'] == ['Ensure this value is greater than or equal to 0.']

    assert not UserQuota.objects.exists()


def test_create_quotas_invalid_amount_not_number(client_api_auth, create_quota_data, url):

    create_quota_data['amount'] = '10A0.1'

    response = client_api_auth.post(url, data=create_quota_data)

    assert response.status_code == HTTPStatus.BAD_REQUEST

    body = response.json()

    assert body['errors'] == ['Enter a whole number.']

    assert not UserQuota.objects.exists()


def test_create_quotas_invalid_price(client_api_auth, create_quota_data, url):

    create_quota_data['price'] = '100.00.0'

    response = client_api_auth.post(url, data=create_quota_data)

    assert response.status_code == HTTPStatus.BAD_REQUEST

    body = response.json()

    assert body['errors'] == ['Enter a number.']

    assert not UserQuota.objects.exists()


def test_create_quotas_invalid_service_choices(client_api_auth, create_quota_data, url):

    create_quota_data['service_type'] = 'AA'

    response = client_api_auth.post(url, data=create_quota_data)

    assert response.status_code == HTTPStatus.BAD_REQUEST

    body = response.json()

    assert body['errors'] == ['Select a valid choice. AA is not one of the available choices.']

    assert not UserQuota.objects.exists()


def test_read_quotas(client_api_auth, user_quotas, url):
    '''
    endpoint: /api/v1/users/<uuid>/quotas/ - GET
    '''

    response = client_api_auth.get(url)

    body = response.json()

    assert response.status_code == HTTPStatus.OK

    quota_db_list = list(UserQuota.objects.filter(user=user_quotas.user))

    quota_response_list = body['quotas']

    assert len(quota_response_list) == len(quota_db_list)

    for quota_response, quota_db in zip(quota_response_list, quota_db_list):
        assert quota_response['amount'] ==  quota_db.amount
        assert quota_response['price'] ==  quota_db.price
        assert quota_response['service_type'] ==  quota_db.get_service_type_display()
        assert quota_response['status_payment'] ==  quota_db.get_status_payment_display()
        assert quota_response['id'] ==  str(quota_db.uuid)
        assert quota_response['user_id'] ==  str(quota_db.user.uuid)
        assert quota_response['created_at'] == str(quota_db.created_at.date())

def test_try_to_read_quotas_for_user_without_qoutas(client_api_auth, user, url):
    '''
    endpoint: /api/v1/users/<uuid>/quotas/ - GET
    '''

    response = client_api_auth.get(url)

    assert response.status_code == HTTPStatus.NOT_FOUND

    body = response.json()

    assert body == {'errors': ['This user has no quota record.']}


# def test_update_quotas(client_api_auth, user, url):
#     '''
#     endpoint: /api/v1/users/<uuid>/quotas/ - PATCH

#     request body:

#     {
#         "clinic_dosimetry": "20"
#     }

#     '''

#     UserQuota.objects.create(user=user, clinic_dosimetry=2)

#     quota = UserQuota.objects.first()

#     assert quota.clinic_dosimetry == 2

#     payload = {'clinic_dosimetry': 20}

#     response = client_api_auth.patch(url, data=payload)

#     assert response.status_code == HTTPStatus.NO_CONTENT

#     quota = UserQuota.objects.first()

#     assert quota.clinic_dosimetry == payload['clinic_dosimetry']


# def test_try_to_update_quotas_for_user_without_qoutas(client_api_auth, user, url):
#     '''
#     endpoint: /api/v1/users/<uuid>/quotas/ - PATCH

#     request body:

#     {
#         "clinic_dosimetry": "20"
#     }

#     '''

#     payload = {'clinic_dosimetry': 20}

#     response = client_api_auth.patch(url, data=payload)

#     assert response.status_code == HTTPStatus.NOT_FOUND

#     body = response.json()

#     assert body == {'errors': ['This user has no quota record.']}


# def test_try_to_update_quotas_negative_number(client_api_auth, user, url):
#     '''
#     endpoint: /api/v1/users/<uuid>/quotas/ - PATCH

#     request body:

#     {
#         "clinic_dosimetry": "20"
#     }

#     '''

#     UserQuota.objects.create(user=user, clinic_dosimetry=2)

#     quota = UserQuota.objects.first()

#     assert quota.clinic_dosimetry == 2

#     payload = {'clinic_dosimetry': -20}

#     response = client_api_auth.patch(url, data=payload)

#     assert response.status_code == HTTPStatus.BAD_REQUEST

#     body = response.json()

#     assert body['errors'] == ['Ensure this value is greater than or equal to 0.']

#     quota = UserQuota.objects.first()

#     assert quota.clinic_dosimetry == 2


# def test_update_must_be_at_least_one_field_valid(client_api_auth, user, url):
#     '''
#     endpoint: /api/v1/users/<uuid>/quotas/ - PATCH

#     request body:

#     {
#         "clinic_dosimetry": "20"
#     }

#     '''

#     payload = {'dosimetry': 20}

#     response = client_api_auth.patch(url, data=payload)

#     assert response.status_code == HTTPStatus.BAD_REQUEST

#     body = response.json()

#     assert body == {'errors': ['Must be at least once in these fields: [clinic_dosimetry]']}


# def test_delete_user_qoutes(client_api_auth, user, url):
#     '''
#     endpoint: /api/v1/users/<uuid>/quotas/ - DELETE

#     no request body:

#     '''

#     UserQuota.objects.create(user=user, clinic_dosimetry=2)

#     assert UserQuota.objects.exists()

#     response = client_api_auth.delete(url)

#     assert response.status_code == HTTPStatus.NO_CONTENT

#     assert not UserQuota.objects.exists()


# def test_try_to_delete_user_qoutes_for_user_without_qoutas(client_api_auth, user, url):
#     '''
#     endpoint: /api/v1/users/<uuid>/quotas/ - DELETE

#     no request body:

#     '''

#     response = client_api_auth.delete(url)

#     assert response.status_code == HTTPStatus.NOT_FOUND

#     body = response.json()

#     assert body['errors'] == ['This user has no quota record.']


# def test_token_and_user_id_dont_match(client_api_auth, user, url):

#     UserQuota.objects.create(user=user, clinic_dosimetry=2)

#     url = resolve_url('api:quotas', uuid4())
#     response = client_api_auth.get(url)

#     assert response.status_code == HTTPStatus.UNAUTHORIZED

#     body = response.json()

#     assert body['errors'] == ['Token and User id do not match.']
