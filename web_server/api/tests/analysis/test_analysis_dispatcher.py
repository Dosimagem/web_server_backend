from http import HTTPStatus

from django.shortcuts import resolve_url

from web_server.core.errors_msg import MSG_ERROR_TOKEN_USER


def test_list_create_analysis_not_allowed_method(client_api_auth, user, clinic_order):
    '''
    /api/v1/users/<uuid>/order/<uuid>/analysis/ - GET, POST
    '''

    url = resolve_url('api:analysis-list-create', user.uuid, clinic_order.uuid)

    resp = client_api_auth.put(url)
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    resp = client_api_auth.patch(url)
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    resp = client_api_auth.delete(url)
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED


def test_list_create_token_id_and_user_id_dont_match(client_api, user, second_user, clinic_order):
    '''
    /api/v1/users/<uuid>/order/<uuid>/analysis/ - GET, POST
    The token does not belong to the user
    '''

    client_api.credentials(HTTP_AUTHORIZATION='Bearer ' + user.auth_token.key)

    url = resolve_url('api:analysis-list-create', second_user.uuid, clinic_order.uuid)
    response = client_api.get(url)

    assert response.status_code == HTTPStatus.UNAUTHORIZED

    body = response.json()

    assert body['errors'] == MSG_ERROR_TOKEN_USER


def test_list_create_analysis_auth(client_api, user, clinic_order):
    '''
    /api/v1/users/<uuid>/order/<uuid>/analysis/ - GET, POST
    '''

    url = resolve_url('api:analysis-list-create', user.uuid, clinic_order.uuid)

    resp = client_api.get(url)
    assert resp.status_code == HTTPStatus.UNAUTHORIZED

    body = resp.json()

    assert body['detail'] == 'As credenciais de autenticação não foram fornecidas.'


def test_read_update_delete_analysis_not_allowed_method(client_api_auth, clinic_dosimetry):
    '''
    /api/v1/users/<uuid>/order/<uuid>/analysis/<uuid> - GET, DELETE, UPDATE
    '''

    user_uuid = clinic_dosimetry.user.uuid
    order_uuid = clinic_dosimetry.order.uuid
    analysis_uuid = clinic_dosimetry.uuid

    url = resolve_url('api:analysis-read-update-delete', user_uuid, order_uuid, analysis_uuid)

    resp = client_api_auth.post(url)
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED


def test_read_update_delete_view_token_and_user_id_dont_match(client_api, second_user, clinic_dosimetry):
    '''
    /api/v1/users/<uuid>/order/<uuid>/analysis/<uuid> - GET, DELETE, UPDATE
    The token does not belong to the user
    '''

    user_uuid = clinic_dosimetry.user.uuid
    order_uuid = clinic_dosimetry.order.uuid
    analysis_uuid = clinic_dosimetry.uuid

    client_api.credentials(HTTP_AUTHORIZATION='Bearer ' + second_user.auth_token.key)

    url = resolve_url('api:analysis-read-update-delete', user_uuid, order_uuid, analysis_uuid)
    response = client_api.get(url)

    assert response.status_code == HTTPStatus.UNAUTHORIZED

    body = response.json()

    assert body['errors'] == MSG_ERROR_TOKEN_USER


def test_read_update_delete_analysis_auth(client_api, second_user, clinic_dosimetry):
    '''
    /api/v1/users/<uuid>/order/<uuid>/analysis/<uuid> - GET, DELETE, UPDATE
    '''

    user_uuid = clinic_dosimetry.user.uuid
    order_uuid = clinic_dosimetry.order.uuid
    analysis_uuid = clinic_dosimetry.uuid

    url = resolve_url('api:analysis-read-update-delete', user_uuid, order_uuid, analysis_uuid)

    resp = client_api.get(url)

    assert resp.status_code == HTTPStatus.UNAUTHORIZED

    body = resp.json()

    assert body['detail'] == 'As credenciais de autenticação não foram fornecidas.'
