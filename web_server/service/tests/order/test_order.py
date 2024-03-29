from http import HTTPStatus
from uuid import uuid4

from django.shortcuts import resolve_url

from web_server.core.errors_msg import MSG_ERROR_RESOURCE, MSG_ERROR_TOKEN_USER
from web_server.service.models import Order
from web_server.service.order_svc import OrderInfos

# List - GET


def test_list_orders_of_user(client_api_auth, user, clinic_order, preclinic_order, segmentation_order):
    """
    /api/v1/users/<uuid>/orders/ - GET
    """

    url = resolve_url('service:order-list', user.uuid)

    response = client_api_auth.get(url)

    body = response.json()

    assert response.status_code == HTTPStatus.OK

    order_db_list = list(Order.objects.filter(user=user))

    order_response_list = body['row']

    assert body['count'] == len(order_db_list)

    for order_response, order_db in zip(order_response_list, order_db_list):

        order_analysis_infos = OrderInfos(order_db).analysis_status_count()

        assert order_response['id'] == str(order_db.uuid)
        assert order_response['userId'] == str(order_db.user.uuid)
        assert order_response['quantityOfAnalyzes'] == order_db.quantity_of_analyzes
        assert order_response['remainingOfAnalyzes'] == order_db.remaining_of_analyzes
        assert order_response['price'] == order_db.price
        assert order_response['serviceName'] == order_db.get_service_name_display()
        assert order_response['statusPayment'] == order_db.get_status_payment_display()
        assert order_response['createdAt'] == str(order_db.created_at.date())
        assert order_response['active'] == order_db.active
        assert order_response['code'] == order_db.code
        assert order_response['billUrl'] is None

        assert order_response['analysisStatus']['concluded'] == order_analysis_infos['concluded']
        assert order_response['analysisStatus']['processing'] == order_analysis_infos['processing']
        assert order_response['analysisStatus']['analyzingInfos'] == order_analysis_infos['analyzing_infos']


def test_try_list_orders_for_user_without_order(client_api_auth, user):
    """
    /api/v1/users/<uuid>/orders/ - GET
    """

    url = resolve_url('service:order-list', user.uuid)

    response = client_api_auth.get(url)

    assert response.status_code == HTTPStatus.OK

    body = response.json()

    assert body == {'row': [], 'count': 0}


def test_list_not_allowed_method(client_api_auth, clinic_order):

    url = resolve_url('service:order-list', clinic_order.user.uuid)

    resp = client_api_auth.post(url, format='json')
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    resp = client_api_auth.put(url, format='json')
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    resp = client_api_auth.patch(url, format='json')
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    resp = client_api_auth.delete(url, format='json')
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED


def test_list_token_view_and_user_id_dont_match(client_api_auth, clinic_order):
    """
    The token does not belong to the user
    """

    url = resolve_url('service:order-list', uuid4())
    response = client_api_auth.get(url)

    assert response.status_code == HTTPStatus.UNAUTHORIZED

    body = response.json()

    assert body['errors'] == MSG_ERROR_TOKEN_USER


# Read - GET


def test_read_order_by_id(client_api_auth, clinic_order):
    """
    /api/v1/users/<uuid>/orders/<uuid> - GET
    """

    url = resolve_url('service:order-read', user_id=clinic_order.user.uuid, order_id=clinic_order.uuid)

    response = client_api_auth.get(url)

    assert response.status_code == HTTPStatus.OK

    body = response.json()

    order_db = Order.objects.get(id=clinic_order.id)

    order_analysis_infos = OrderInfos(order_db).analysis_status_count()

    assert body['id'] == str(order_db.uuid)
    assert body['userId'] == str(order_db.user.uuid)
    assert body['quantityOfAnalyzes'] == order_db.quantity_of_analyzes
    assert body['remainingOfAnalyzes'] == order_db.remaining_of_analyzes
    assert body['price'] == order_db.price
    assert body['serviceName'] == order_db.get_service_name_display()
    assert body['statusPayment'] == order_db.get_status_payment_display()
    assert body['createdAt'] == str(order_db.created_at.date())
    assert body['active'] == order_db.active
    assert body['code'] == order_db.code
    assert body['billUrl'] is None

    assert body['analysisStatus']['concluded'] == order_analysis_infos['concluded']
    assert body['analysisStatus']['processing'] == order_analysis_infos['processing']
    assert body['analysisStatus']['analyzingInfos'] == order_analysis_infos['analyzing_infos']


def test_read_order_by_wrong_id(client_api_auth, clinic_order):
    """
    /api/v1/users/<uuid>/orders/<uuid> - GET
    """

    url = resolve_url('service:order-read', user_id=clinic_order.user.uuid, order_id=uuid4())

    response = client_api_auth.get(url)

    assert response.status_code == HTTPStatus.NOT_FOUND

    body = response.json()

    assert body['errors'] == MSG_ERROR_RESOURCE


def test_try_read_order_for_user_without_order(client_api_auth, user):
    """
    /api/v1/users/<uuid>/orders/<uuid> - GET

    The user does not have a order registration
    """

    url = resolve_url('service:order-read', user_id=user.uuid, order_id=uuid4())

    response = client_api_auth.get(url)

    assert response.status_code == HTTPStatus.NOT_FOUND

    body = response.json()

    assert body['errors'] == MSG_ERROR_RESOURCE


def test_read_view_token_and_user_id_dont_match(client_api_auth, clinic_order):
    """
    The token does not belong to the user
    """

    url = resolve_url('service:order-read', user_id=uuid4(), order_id=clinic_order.uuid)

    response = client_api_auth.get(url)

    assert response.status_code == HTTPStatus.UNAUTHORIZED

    body = response.json()

    assert body['errors'] == MSG_ERROR_TOKEN_USER


def test_read_not_allowed_method(client_api_auth, clinic_order):

    url = resolve_url('service:order-read', user_id=clinic_order.user.uuid, order_id=clinic_order.uuid)

    resp = client_api_auth.post(url, format='json')
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    resp = client_api_auth.put(url, format='json')
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    resp = client_api_auth.patch(url, format='json')
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    resp = client_api_auth.delete(url, format='json')
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED
