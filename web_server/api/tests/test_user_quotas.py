from decimal import Decimal
from http import HTTPStatus
from uuid import uuid4

import pytest
from django.shortcuts import resolve_url

from web_server.service.models import UserQuota


@pytest.fixture
def url(user):
    return resolve_url('api:create-list', user.uuid)


# CREATE - POST

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


def test_invalid_create_quotas_negative_amount(client_api_auth, create_quota_data, url):
    '''
    endpoint: /api/v1/users/<uuid>/quotas/ - POST
    '''

    create_quota_data['amount'] = -10

    response = client_api_auth.post(url, data=create_quota_data)

    assert response.status_code == HTTPStatus.BAD_REQUEST

    body = response.json()

    assert body['errors'] == ['Ensure this value is greater than or equal to 0.']

    assert not UserQuota.objects.exists()


def test_invalid_create_quotas_amount_is_not_number(client_api_auth, create_quota_data, url):

    create_quota_data['amount'] = '10A0.1'

    response = client_api_auth.post(url, data=create_quota_data)

    assert response.status_code == HTTPStatus.BAD_REQUEST

    body = response.json()

    assert body['errors'] == ['Enter a whole number.']

    assert not UserQuota.objects.exists()


def test_invalid_create_quotas_price_is_not_number(client_api_auth, create_quota_data, url):

    create_quota_data['price'] = '100.00.0'

    response = client_api_auth.post(url, data=create_quota_data)

    assert response.status_code == HTTPStatus.BAD_REQUEST

    body = response.json()

    assert body['errors'] == ['Enter a number.']

    assert not UserQuota.objects.exists()


def test_invalid_create_quotas_service_choices(client_api_auth, create_quota_data, url):

    create_quota_data['service_type'] = 'AA'

    response = client_api_auth.post(url, data=create_quota_data)

    assert response.status_code == HTTPStatus.BAD_REQUEST

    body = response.json()

    assert body['errors'] == ['Select a valid choice. AA is not one of the available choices.']

    assert not UserQuota.objects.exists()


# List - GET

def test_list_quotas_of_user(client_api_auth, user_and_quota, url):
    '''
    endpoint: /api/v1/users/<uuid>/quotas/ - GET
    '''

    response = client_api_auth.get(url)

    body = response.json()

    assert response.status_code == HTTPStatus.OK

    quota_db_list = list(UserQuota.objects.filter(user=user_and_quota.user))

    quota_response_list = body['quotas']

    assert len(quota_response_list) == len(quota_db_list)

    for quota_response, quota_db in zip(quota_response_list, quota_db_list):
        assert quota_response['amount'] == quota_db.amount
        assert quota_response['price'] == quota_db.price
        assert quota_response['service_type'] == quota_db.get_service_type_display()
        assert quota_response['status_payment'] == quota_db.get_status_payment_display()
        assert quota_response['id'] == str(quota_db.uuid)
        assert quota_response['user_id'] == str(quota_db.user.uuid)
        assert quota_response['created_at'] == str(quota_db.created_at.date())


def test_try_list_quotas_for_user_without_qoutas(client_api_auth, user, url):
    '''
    endpoint: /api/v1/users/<uuid>/quotas/ - GET
    '''

    response = client_api_auth.get(url)

    assert response.status_code == HTTPStatus.NOT_FOUND

    body = response.json()

    assert body == {'errors': ['This user has no quota record.']}


def test_read_quota_by_id(client_api_auth, user_and_quota):
    '''
    endpoint: /api/v1/users/<uuid>/quotas/<uuid> - GET
    '''

    url = resolve_url('api:read-patch-delete', user_id=user_and_quota.user.uuid, quota_id=user_and_quota.uuid)

    response = client_api_auth.get(url)

    assert response.status_code == HTTPStatus.OK

    body = response.json()

    quota_db = UserQuota.objects.get(id=user_and_quota.id)

    assert body['amount'] == quota_db.amount
    assert body['price'] == quota_db.price
    assert body['service_type'] == quota_db.get_service_type_display()
    assert body['status_payment'] == quota_db.get_status_payment_display()
    assert body['id'] == str(quota_db.uuid)
    assert body['user_id'] == str(quota_db.user.uuid)
    assert body['created_at'] == str(quota_db.created_at.date())


def test_read_quota_by_wrong_id(client_api_auth, user_and_quota):
    '''
    endpoint: /api/v1/users/<uuid>/quotas/<uuid> - GET
    '''

    url = resolve_url('api:read-patch-delete', user_id=user_and_quota.user.uuid, quota_id=uuid4())

    response = client_api_auth.get(url)

    assert response.status_code == HTTPStatus.NOT_FOUND

    body = response.json()

    assert body['errors'] == ['There is no information for this pair of ids']


def test_try_read_quota_for_user_without_qoutas(client_api_auth, user, url):
    '''
    endpoint: /api/v1/users/<uuid>/quotas/<uuid> - GET

    The user does not have a quota registration
    '''

    url = resolve_url('api:read-patch-delete', user_id=user.uuid, quota_id=uuid4())

    response = client_api_auth.get(url)

    assert response.status_code == HTTPStatus.NOT_FOUND

    body = response.json()

    assert body == {'errors': ['This user has no quota record.']}


# Update - PATCH

def test_update_quota_amount(client_api_auth, user_and_quota):
    '''
    endpoint: /api/v1/users/<uuid>/quotas/<uuid> - PATCH
    '''

    quota = UserQuota.objects.first()

    assert quota.amount == 10

    payload = {'amount': 20}

    url = resolve_url('api:read-patch-delete', user_id=user_and_quota.user.uuid, quota_id=user_and_quota.uuid)

    response = client_api_auth.patch(url, data=payload)

    assert response.status_code == HTTPStatus.NO_CONTENT

    quota = UserQuota.objects.first()

    assert quota.amount == payload['amount']


def test_invalid_update_quota_negative_amount(client_api_auth, user_and_quota):
    '''
    endpoint: /api/v1/users/<uuid>/quotas/<uuid> - PATCH
    '''

    quota_db = UserQuota.objects.first()

    assert quota_db.amount == user_and_quota.amount

    url = resolve_url('api:read-patch-delete', user_id=user_and_quota.user.uuid, quota_id=user_and_quota.uuid)

    response = client_api_auth.patch(url, data={'amount': -20})

    assert response.status_code == HTTPStatus.BAD_REQUEST

    body = response.json()

    quota_db = UserQuota.objects.first()

    assert quota_db.amount == user_and_quota.amount

    assert body['errors'] == ['Ensure this value is greater than or equal to 0.']


def test_invalid_update_quota_empty_body(client_api_auth, user_and_quota):
    '''
    endpoint: /api/v1/users/<uuid>/quotas/<uuid> - PATCH
    '''

    quota_db = UserQuota.objects.first()

    assert quota_db.amount == user_and_quota.amount

    url = resolve_url('api:read-patch-delete', user_id=user_and_quota.user.uuid, quota_id=user_and_quota.uuid)

    response = client_api_auth.patch(url)

    assert response.status_code == HTTPStatus.BAD_REQUEST

    body = response.json()

    quota_db = UserQuota.objects.first()

    assert quota_db.amount == user_and_quota.amount

    assert body['errors'] == ['Amount field is required.']


# Delete - delete


def test_delete_user_qoutes(client_api_auth, user_and_quota):
    '''
    endpoint: /api/v1/users/<uuid>/quotas/<uuid> - DELETE
    '''

    url = resolve_url('api:read-patch-delete', user_id=user_and_quota.user.uuid, quota_id=user_and_quota.uuid)

    response = client_api_auth.delete(url)

    assert response.status_code == HTTPStatus.NO_CONTENT

    assert not UserQuota.objects.exists()


# def test_try_to_delete_user_qoutes_for_user_without_qoutas(client_api_auth, user, url):
#     '''
#     endpoint: /api/v1/users/<uuid>/quotas/ - DELETE

#     no request body:

#     '''

#     response = client_api_auth.delete(url)

#     assert response.status_code == HTTPStatus.NOT_FOUND

#     body = response.json()

#     assert body['errors'] == ['This user has no quota record.']


def test_create_list_token_view_and_user_id_dont_match(client_api_auth, user_and_quota):
    '''
    The token does not belong to the user
    '''

    url = resolve_url('api:create-list', uuid4())
    response = client_api_auth.get(url)

    assert response.status_code == HTTPStatus.UNAUTHORIZED

    body = response.json()

    assert body['errors'] == ['Token and User id do not match.']


def test_read_patch_delete_view_token_and_user_id_dont_match(client_api_auth, user_and_quota):
    '''
    The token does not belong to the user
    '''

    url = resolve_url('api:read-patch-delete', user_id=uuid4(), quota_id=user_and_quota.uuid)

    response = client_api_auth.get(url)

    assert response.status_code == HTTPStatus.UNAUTHORIZED

    body = response.json()

    assert body['errors'] == ['Token and User id do not match.']
