from http import HTTPStatus
from uuid import uuid4

from django.shortcuts import resolve_url

from web_server.service.models import Order
from web_server.api.views.errors_msg import (
    MSG_ERROR_TOKEN_USER,
    MSG_ERROR_RESOURCE,
    MSG_ERROR_USER_ORDER,
)


# List - GET

def test_list_orders_of_user(client_api_auth, user_and_order):
    '''
    /api/v1/users/<uuid>/orders/ - GET
    '''

    url = resolve_url('api:order-list', user_and_order.user.uuid)

    response = client_api_auth.get(url)

    body = response.json()

    assert response.status_code == HTTPStatus.OK

    order_db_list = list(Order.objects.filter(user=user_and_order.user))

    order_response_list = body['orders']

    assert len(order_response_list) == len(order_db_list)

    for order_response, order_db in zip(order_response_list, order_db_list):
        assert order_response['id'] == str(order_db.uuid)
        assert order_response['userId'] == str(order_db.user.uuid)
        assert order_response['quantityOfAnalyzes'] == order_db.quantity_of_analyzes
        assert order_response['remainingOfAnalyzes'] == order_db.remaining_of_analyzes
        assert order_response['price'] == order_db.price
        assert order_response['serviceName'] == order_db.get_service_name_display()
        assert order_response['statusPayment'] == order_db.get_status_payment_display()
        assert order_response['createdAt'] == str(order_db.created_at.date())
        assert order_response['permission'] == order_db.permission


def test_try_list_orders_for_user_without_order(client_api_auth, user):
    '''
    /api/v1/users/<uuid>/orders/ - GET
    '''

    url = resolve_url('api:order-list', user.uuid)

    response = client_api_auth.get(url)

    assert response.status_code == HTTPStatus.NOT_FOUND

    body = response.json()

    assert body == {'errors': MSG_ERROR_USER_ORDER}


def test_list_not_allowed_method(client_api_auth, user_and_order):

    url = resolve_url('api:order-list', user_and_order.user.uuid)

    resp = client_api_auth.post(url, format='json')
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    resp = client_api_auth.put(url, format='json')
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    resp = client_api_auth.patch(url, format='json')
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    resp = client_api_auth.delete(url, format='json')
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED


def test_list_token_view_and_user_id_dont_match(client_api_auth, user_and_order):
    '''
    The token does not belong to the user
    '''

    url = resolve_url('api:order-list', uuid4())
    response = client_api_auth.get(url)

    assert response.status_code == HTTPStatus.UNAUTHORIZED

    body = response.json()

    assert body['errors'] == MSG_ERROR_TOKEN_USER


# Read - GET


def test_read_order_by_id(client_api_auth, user_and_order):
    '''
    /api/v1/users/<uuid>/orders/<uuid> - GET
    '''

    url = resolve_url('api:order-read', user_id=user_and_order.user.uuid, order_id=user_and_order.uuid)

    response = client_api_auth.get(url)

    assert response.status_code == HTTPStatus.OK

    body = response.json()

    order_db = Order.objects.get(id=user_and_order.id)

    assert body['id'] == str(order_db.uuid)
    assert body['userId'] == str(order_db.user.uuid)
    assert body['quantityOfAnalyzes'] == order_db.quantity_of_analyzes
    assert body['remainingOfAnalyzes'] == order_db.remaining_of_analyzes
    assert body['price'] == order_db.price
    assert body['serviceName'] == order_db.get_service_name_display()
    assert body['statusPayment'] == order_db.get_status_payment_display()
    assert body['createdAt'] == str(order_db.created_at.date())
    assert body['permission'] == order_db.permission


def test_read_order_by_wrong_id(client_api_auth, user_and_order):
    '''
    /api/v1/users/<uuid>/orders/<uuid> - GET
    '''

    url = resolve_url('api:order-read', user_id=user_and_order.user.uuid, order_id=uuid4())

    response = client_api_auth.get(url)

    assert response.status_code == HTTPStatus.NOT_FOUND

    body = response.json()

    assert body['errors'] == MSG_ERROR_RESOURCE


def test_try_read_order_for_user_without_order(client_api_auth, user):
    '''
    /api/v1/users/<uuid>/orders/<uuid> - GET

    The user does not have a order registration
    '''

    url = resolve_url('api:order-read', user_id=user.uuid, order_id=uuid4())

    response = client_api_auth.get(url)

    assert response.status_code == HTTPStatus.NOT_FOUND

    body = response.json()

    assert body == {'errors': MSG_ERROR_USER_ORDER}


def test_read_view_token_and_user_id_dont_match(client_api_auth, user_and_order):
    '''
    The token does not belong to the user
    '''

    url = resolve_url('api:order-read', user_id=uuid4(), order_id=user_and_order.uuid)

    response = client_api_auth.get(url)

    assert response.status_code == HTTPStatus.UNAUTHORIZED

    body = response.json()

    assert body['errors'] == MSG_ERROR_TOKEN_USER


def test_read_not_allowed_method(client_api_auth, user_and_order):

    url = resolve_url('api:order-read', user_id=user_and_order.user.uuid, order_id=user_and_order.uuid)

    resp = client_api_auth.post(url, format='json')
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    resp = client_api_auth.put(url, format='json')
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    resp = client_api_auth.patch(url, format='json')
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    resp = client_api_auth.delete(url, format='json')
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED


# Update - PATCH

# def test_update_order_amount(client_api_auth, user_and_order):
#     '''
#     /api/v1/users/<uuid>/orders/<uuid> - PATCH
#     '''

#     order = Order.objects.first()

#     assert order.amount == 10

#     payload = {'amount': 20}

#     url = resolve_url('api:read-patch-delete', user_id=user_and_order.user.uuid, order_id=user_and_order.uuid)

#     response = client_api_auth.patch(url, data=payload)

#     assert response.status_code == HTTPStatus.NO_CONTENT

#     order = Order.objects.first()

#     assert order.amount == payload['amount']


# def test_invalid_update_order_negative_amount(client_api_auth, user_and_order):
#     '''
#     /api/v1/users/<uuid>/orders/<uuid> - PATCH
#     '''

#     order_db = Order.objects.first()

#     assert order_db.amount == user_and_order.amount

#     url = resolve_url('api:read-patch-delete', user_id=user_and_order.user.uuid, order_id=user_and_order.uuid)

#     response = client_api_auth.patch(url, data={'amount': -20})

#     assert response.status_code == HTTPStatus.BAD_REQUEST

#     body = response.json()

#     order_db = Order.objects.first()

#     assert order_db.amount == user_and_order.amount

#     assert body['errors'] == ['Ensure this value is greater than or equal to 0.']


# def test_invalid_update_order_empty_body(client_api_auth, user_and_order):
#     '''
#     /api/v1/users/<uuid>/orders/<uuid> - PATCH
#     '''

#     order_db = Order.objects.first()

#     assert order_db.amount == user_and_order.amount

#     url = resolve_url('api:read-patch-delete', user_id=user_and_order.user.uuid, order_id=user_and_order.uuid)

#     response = client_api_auth.patch(url)

#     assert response.status_code == HTTPStatus.BAD_REQUEST

#     body = response.json()

#     order_db = Order.objects.first()

#     assert order_db.amount == user_and_order.amount

#     assert body['errors'] == ['Amount field is required.']


# Delete - delete


# def test_delete_user_qoutes(client_api_auth, user_and_order):
#     '''
#     /api/v1/users/<uuid>/orders/<uuid> - DELETE
#     '''

#     url = resolve_url('api:read-patch-delete', user_id=user_and_order.user.uuid, order_id=user_and_order.uuid)

#     response = client_api_auth.delete(url)

#     assert response.status_code == HTTPStatus.NO_CONTENT

#     assert not Order.objects.exists()


# CREATE - POST

# def test_create_orders_successfully_with(client_api_auth, create_order_data, url):
#     '''
#     /api/v1/users/<uuid>/orders/ - POST
#     '''

#     response = client_api_auth.post(url, data=create_order_data)

#     assert response.status_code == HTTPStatus.CREATED

#     body = response.json()

#     assert body['amount'] == create_order_data['amount']
#     assert Decimal(body['price']) == Decimal(create_order_data['price'])
#     assert body['service_type'] == 'Dosimetria Clinica'
#     assert body['status_payment'] == 'Aguardando pagamento'
#     assert 'created_at' in body

#     assert Order.objects.exists()

#     order_db = Order.objects.first()

#     assert order_db.amount == create_order_data['amount']
#     assert order_db.price == Decimal(create_order_data['price'])
#     assert order_db.service_type == Order.DOSIMETRY_CLINIC
#     assert order_db.status_payment == Order.AWAITING_PAYMENT


# def test_invalid_create_orders_negative_amount(client_api_auth, create_order_data, url):
#     '''
#     /api/v1/users/<uuid>/orders/ - POST
#     '''

#     create_order_data['amount'] = -10

#     response = client_api_auth.post(url, data=create_order_data)

#     assert response.status_code == HTTPStatus.BAD_REQUEST

#     body = response.json()

#     assert body['errors'] == ['Ensure this value is greater than or equal to 0.']

#     assert not Order.objects.exists()


# def test_invalid_create_orders_amount_is_not_number(client_api_auth, create_order_data, url):

#     create_order_data['amount'] = '10A0.1'

#     response = client_api_auth.post(url, data=create_order_data)

#     assert response.status_code == HTTPStatus.BAD_REQUEST

#     body = response.json()

#     assert body['errors'] == ['Enter a whole number.']

#     assert not Order.objects.exists()


# def test_invalid_create_orders_price_is_not_number(client_api_auth, create_order_data, url):

#     create_order_data['price'] = '100.00.0'

#     response = client_api_auth.post(url, data=create_order_data)

#     assert response.status_code == HTTPStatus.BAD_REQUEST

#     body = response.json()

#     assert body['errors'] == ['Enter a number.']

#     assert not Order.objects.exists()


# def test_invalid_create_orders_service_choices(client_api_auth, create_order_data, url):

#     create_order_data['service_type'] = 'AA'

#     response = client_api_auth.post(url, data=create_order_data)

#     assert response.status_code == HTTPStatus.BAD_REQUEST

#     body = response.json()

#     assert body['errors'] == ['Select a valid choice. AA is not one of the available choices.']

#     assert not Order.objects.exists()
