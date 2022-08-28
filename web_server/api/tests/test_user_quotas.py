from http import HTTPStatus

from django.shortcuts import resolve_url


from web_server.service.models import UserQuotas


def test_create_quotas_successfully_with(client_api, user):
    '''
    endpoint: /api/v1/users/<uuid>/quotas/ - POST

    body:

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

    no body
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

    body:

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

# def test_read_quotas(client_api, user):

#     client_api.credentials(HTTP_AUTHORIZATION='Bearer ' + user.auth_token.key)

#     url = resolve_url('api:quotas', user.uuid)

#     response = client_api.get(url)

#     assert res
