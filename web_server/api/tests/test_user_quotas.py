from http import HTTPStatus

from django.shortcuts import resolve_url


from web_server.service.models import UserQuotas


def test_create_quotas_successfully_with(client_api, user):
    '''
    endpoint: /api/v1/users/<uuid>/quotas/ - POST

    request body:

    {
        "clinic_dosimetry": "10"
    }
    '''

    payload = {
        'clinic_dosimetry': 10
    }

    client_api.credentials(HTTP_AUTHORIZATION='Bearer ' + user.auth_token.key)

    url = resolve_url('api:quotas', user.uuid)

    response = client_api.post(url, data=payload)

    assert response.status_code == HTTPStatus.CREATED

    body = response.json()

    assert body['clinic_dosimetry'] == payload['clinic_dosimetry']

    assert UserQuotas.objects.exists()


def test_create_quotas_successfully_without_body(client_api, user):
    '''
    endpoint: /api/v1/users/<uuid>/quotas/ - POST

    no request body
    '''

    client_api.credentials(HTTP_AUTHORIZATION='Bearer ' + user.auth_token.key)

    url = resolve_url('api:quotas', user.uuid)

    response = client_api.post(url)

    assert response.status_code == HTTPStatus.CREATED

    body = response.json()

    assert body['clinic_dosimetry'] == 0

    assert UserQuotas.objects.exists()


def test_create_quotas_fail_negative_number(client_api, user):
    '''
    endpoint: /api/v1/users/<uuid>/quotas/ - POST

    request body:

    {
        "clinic_dosimetry": "10"
    }
    '''

    payload = {
        'clinic_dosimetry': -10
    }

    client_api.credentials(HTTP_AUTHORIZATION='Bearer ' + user.auth_token.key)

    url = resolve_url('api:quotas', user.uuid)

    response = client_api.post(url, data=payload)

    assert response.status_code == HTTPStatus.BAD_REQUEST

    body = response.json()

    assert body['errors'] == ['Ensure this value is greater than or equal to 0.']

    assert not UserQuotas.objects.exists()


def test_read_quotas(client_api, user):
    '''
    endpoint: /api/v1/users/<uuid>/quotas/ - GET
    '''

    client_api.credentials(HTTP_AUTHORIZATION='Bearer ' + user.auth_token.key)

    UserQuotas.objects.create(user=user, clinic_dosimetry=2)

    url = resolve_url('api:quotas', user.uuid)

    response = client_api.get(url)

    body = response.json()

    assert response.status_code == HTTPStatus.OK

    assert body['clinic_dosimetry'] == 2


def test_try_to_read_quotas_for_user_without_qoutas(client_api, user):
    '''
    endpoint: /api/v1/users/<uuid>/quotas/ - GET
    '''

    client_api.credentials(HTTP_AUTHORIZATION='Bearer ' + user.auth_token.key)

    url = resolve_url('api:quotas', user.uuid)

    response = client_api.get(url)

    assert response.status_code == HTTPStatus.NOT_FOUND

    body = response.json()

    assert body == {'error': ['This user has no quota record.']}


def test_update_quotas(client_api, user):
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

    payload = {
        'clinic_dosimetry': 20
    }

    client_api.credentials(HTTP_AUTHORIZATION='Bearer ' + user.auth_token.key)

    url = resolve_url('api:quotas', user.uuid)

    response = client_api.patch(url, data=payload)

    assert response.status_code == HTTPStatus.NO_CONTENT

    quota = UserQuotas.objects.first()

    assert quota.clinic_dosimetry == payload['clinic_dosimetry']


def test_try_to_update_quotas_for_user_without_qoutas(client_api, user):
    '''
    endpoint: /api/v1/users/<uuid>/quotas/ - PATCH

    request body:

    {
        "clinic_dosimetry": "20"
    }

    '''

    payload = {
        'clinic_dosimetry': 20
    }

    client_api.credentials(HTTP_AUTHORIZATION='Bearer ' + user.auth_token.key)

    url = resolve_url('api:quotas', user.uuid)

    response = client_api.patch(url, data=payload)

    body = response.json()

    assert body == {'error': ['This user has no quota record.']}


def test_try_to_update_quotas_negative_number(client_api, user):
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

    payload = {
        'clinic_dosimetry': -20
    }

    client_api.credentials(HTTP_AUTHORIZATION='Bearer ' + user.auth_token.key)

    url = resolve_url('api:quotas', user.uuid)

    response = client_api.patch(url, data=payload)

    assert response.status_code == HTTPStatus.BAD_REQUEST

    body = response.json()

    assert body['errors'] == ['Ensure this value is greater than or equal to 0.']

    quota = UserQuotas.objects.first()

    assert quota.clinic_dosimetry == 2
