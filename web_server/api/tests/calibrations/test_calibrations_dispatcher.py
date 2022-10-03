from http import HTTPStatus
from uuid import uuid4

from django.shortcuts import resolve_url

from web_server.api.views.errors_msg import MSG_ERROR_TOKEN_USER


def test_list_create_not_allowed_method(client_api_auth, first_calibration):
    '''
    /api/v1/users/<uuid>/calibrations/ - GET, POST
    '''

    url = resolve_url('api:calibration-list-create', first_calibration.user.uuid)

    resp = client_api_auth.put(url, format='json')
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    resp = client_api_auth.patch(url, format='json')
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    resp = client_api_auth.delete(url, format='json')
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED


def test_list_create_token_id_and_user_id_dont_match(client_api_auth, first_calibration):
    '''
    /api/v1/users/<uuid>/calibrations/ - GET, POST
    The token does not belong to the user
    '''

    url = resolve_url('api:calibration-list-create', uuid4())
    response = client_api_auth.get(url)

    assert response.status_code == HTTPStatus.UNAUTHORIZED

    body = response.json()

    assert body['errors'] == MSG_ERROR_TOKEN_USER


def test_read_update_delete_not_allowed_method(client_api_auth, first_calibration):
    '''
    /api/v1/users/<uuid>/calibrations/<uuid> - GET, PUT, DELETE
    '''

    url = resolve_url('api:calibration-read-update-delete', first_calibration.user.uuid, first_calibration.uuid)

    resp = client_api_auth.patch(url, format='json')
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    resp = client_api_auth.post(url, format='json')
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED


def test_read_update_delete_id_and_user_id_dont_match(client_api_auth, first_calibration):
    '''
    /api/v1/users/<uuid>/calibrations/<uuid> - GET, PUT, DELETE
    The token does not belong to the user
    '''

    url = resolve_url('api:calibration-read-update-delete', uuid4(), first_calibration.uuid)
    response = client_api_auth.get(url)

    assert response.status_code == HTTPStatus.UNAUTHORIZED

    body = response.json()

    assert body['errors'] == MSG_ERROR_TOKEN_USER
