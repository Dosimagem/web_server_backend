from http import HTTPStatus
from uuid import uuid4

import pytest
from django.shortcuts import resolve_url

from web_server.service.models import UserQuotas


@pytest.fixture
def client_api_auth(client_api, user):
    client_api.credentials(HTTP_AUTHORIZATION='Bearer ' + user.auth_token.key)
    return client_api


@pytest.fixture
def url(user):
    return resolve_url('api:quotas', user.uuid)


def test_create_quotas_successfully_with(client_api_auth, url):
    '''
    endpoint: /api/v1/users/<uuid>/quotas/ - POST

    request body:

    {
        "clinic_dosimetry": "10"
    }
    '''

    payload = {'clinic_dosimetry': 10}

    response = client_api_auth.post(url, data=payload)

    assert response.status_code == HTTPStatus.CREATED

    body = response.json()

    assert body['clinic_dosimetry'] == payload['clinic_dosimetry']

    assert UserQuotas.objects.exists()


def test_create_quotas_successfully_without_body(client_api_auth, url):
    '''
    endpoint: /api/v1/users/<uuid>/quotas/ - POST

    no request body
    '''

    response = client_api_auth.post(url)

    assert response.status_code == HTTPStatus.CREATED

    body = response.json()

    assert body['clinic_dosimetry'] == 0

    assert UserQuotas.objects.exists()


def test_create_quotas_fail_negative_number(client_api_auth, url):
    '''
    endpoint: /api/v1/users/<uuid>/quotas/ - POST

    request body:

    {
        "clinic_dosimetry": "10"
    }
    '''

    payload = {'clinic_dosimetry': -10}

    response = client_api_auth.post(url, data=payload)

    assert response.status_code == HTTPStatus.BAD_REQUEST

    body = response.json()

    assert body['errors'] == ['Ensure this value is greater than or equal to 0.']

    assert not UserQuotas.objects.exists()


def test_try_create_quotas_same_user(client_api_auth, url):
    '''
    Must be only one quota row per user.
    '''

    response = client_api_auth.post(url)

    assert response.status_code == HTTPStatus.CREATED

    assert UserQuotas.objects.count() == 1

    response = client_api_auth.post(url)

    assert response.status_code == HTTPStatus.BAD_REQUEST

    assert response.json() == {'errors': ['This user already have quota register']}

    assert UserQuotas.objects.count() == 1


def test_read_quotas(client_api_auth, url, user):
    '''
    endpoint: /api/v1/users/<uuid>/quotas/ - GET
    '''

    UserQuotas.objects.create(user=user, clinic_dosimetry=2)

    response = client_api_auth.get(url)

    body = response.json()

    assert response.status_code == HTTPStatus.OK

    assert body['clinic_dosimetry'] == 2


def test_try_to_read_quotas_for_user_without_qoutas(client_api_auth, user, url):
    '''
    endpoint: /api/v1/users/<uuid>/quotas/ - GET
    '''

    response = client_api_auth.get(url)

    assert response.status_code == HTTPStatus.NOT_FOUND

    body = response.json()

    assert body == {'errors': ['This user has no quota record.']}


def test_update_quotas(client_api_auth, user, url):
    '''
    endpoint: /api/v1/users/<uuid>/quotas/ - PATCH

    request body:

    {
        "clinic_dosimetry": "20"
    }

    '''

    UserQuotas.objects.create(user=user, clinic_dosimetry=2)

    quota = UserQuotas.objects.first()

    assert quota.clinic_dosimetry == 2

    payload = {'clinic_dosimetry': 20}

    response = client_api_auth.patch(url, data=payload)

    assert response.status_code == HTTPStatus.NO_CONTENT

    quota = UserQuotas.objects.first()

    assert quota.clinic_dosimetry == payload['clinic_dosimetry']


def test_try_to_update_quotas_for_user_without_qoutas(client_api_auth, user, url):
    '''
    endpoint: /api/v1/users/<uuid>/quotas/ - PATCH

    request body:

    {
        "clinic_dosimetry": "20"
    }

    '''

    payload = {'clinic_dosimetry': 20}

    response = client_api_auth.patch(url, data=payload)

    assert response.status_code == HTTPStatus.NOT_FOUND

    body = response.json()

    assert body == {'errors': ['This user has no quota record.']}


def test_try_to_update_quotas_negative_number(client_api_auth, user, url):
    '''
    endpoint: /api/v1/users/<uuid>/quotas/ - PATCH

    request body:

    {
        "clinic_dosimetry": "20"
    }

    '''

    UserQuotas.objects.create(user=user, clinic_dosimetry=2)

    quota = UserQuotas.objects.first()

    assert quota.clinic_dosimetry == 2

    payload = {'clinic_dosimetry': -20}

    response = client_api_auth.patch(url, data=payload)

    assert response.status_code == HTTPStatus.BAD_REQUEST

    body = response.json()

    assert body['errors'] == ['Ensure this value is greater than or equal to 0.']

    quota = UserQuotas.objects.first()

    assert quota.clinic_dosimetry == 2


def test_update_must_be_at_least_one_field_valid(client_api_auth, user, url):
    '''
    endpoint: /api/v1/users/<uuid>/quotas/ - PATCH

    request body:

    {
        "clinic_dosimetry": "20"
    }

    '''

    payload = {'dosimetry': 20}

    response = client_api_auth.patch(url, data=payload)

    assert response.status_code == HTTPStatus.BAD_REQUEST

    body = response.json()

    assert body == {'errors': ['Must be at least once in these fields: [clinic_dosimetry]']}


def test_delete_user_qoutes(client_api_auth, user, url):
    '''
    endpoint: /api/v1/users/<uuid>/quotas/ - DELETE

    no request body:

    '''

    UserQuotas.objects.create(user=user, clinic_dosimetry=2)

    assert UserQuotas.objects.exists()

    response = client_api_auth.delete(url)

    assert response.status_code == HTTPStatus.NO_CONTENT

    assert not UserQuotas.objects.exists()


def test_try_to_delete_user_qoutes_for_user_without_qoutas(client_api_auth, user, url):
    '''
    endpoint: /api/v1/users/<uuid>/quotas/ - DELETE

    no request body:

    '''

    response = client_api_auth.delete(url)

    assert response.status_code == HTTPStatus.NOT_FOUND

    body = response.json()

    assert body['errors'] == ['This user has no quota record.']


def test_token_and_user_id_dont_match(client_api_auth, user, url):

    UserQuotas.objects.create(user=user, clinic_dosimetry=2)

    url = resolve_url('api:quotas', uuid4())
    response = client_api_auth.get(url)

    assert response.status_code == HTTPStatus.UNAUTHORIZED

    body = response.json()

    assert body['errors'] == ['Token and User id do not match.']
