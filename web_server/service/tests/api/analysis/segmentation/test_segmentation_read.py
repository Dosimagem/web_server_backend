from http import HTTPStatus
from uuid import uuid4

from django.shortcuts import resolve_url

from web_server.service.models import FORMAT_DATE, Order, SegmentationAnalysis

# /api/v1/users/<uuid>/order/<uuid>/analysis/<uuid> - GET


def test_successfull(client_api_auth, segmentation_analysis):

    user = segmentation_analysis.order.user
    order = segmentation_analysis.order

    url = resolve_url('service:analysis-read-update-delete', user.uuid, order.uuid, segmentation_analysis.uuid)
    resp = client_api_auth.get(url)
    analysis_db = SegmentationAnalysis.objects.get(id=segmentation_analysis.id)

    assert resp.status_code == HTTPStatus.OK

    body = resp.json()

    assert body['id'] == str(analysis_db.uuid)
    assert body['userId'] == str(analysis_db.order.user.uuid)
    assert body['orderId'] == str(analysis_db.order.uuid)
    assert body['status'] == analysis_db.get_status_display()
    assert body['active'] == analysis_db.active
    assert body['serviceName'] == analysis_db.order.get_service_name_display()
    assert body['createdAt'] == analysis_db.created_at.strftime(FORMAT_DATE)
    assert body['modifiedAt'] == analysis_db.modified_at.strftime(FORMAT_DATE)

    # TODO: Pensar uma forma melhor
    assert body['imagesUrl'].startswith(f'http://testserver/media/{analysis_db.order.user.id}/segmentation_analysis')


def test_fail_wrong_analysis_id(client_api_auth, segmentation_analysis):

    user_uuid = segmentation_analysis.order.user.uuid
    order_uuid = segmentation_analysis.order.uuid
    analysis_uuid = uuid4()

    url = resolve_url('service:analysis-read-update-delete', user_uuid, order_uuid, analysis_uuid)
    resp = client_api_auth.get(url)
    body = resp.json()

    assert resp.status_code == HTTPStatus.NOT_FOUND

    assert body['errors'] == ['Este usuário não possui este recurso cadastrado.']


def test_fail_read_using_another_order(client_api_auth, user, segmentation_analysis, create_order_data):

    order = Order.objects.create(
        user=user,
        quantity_of_analyzes=create_order_data['quantity_of_analyzes'],
        remaining_of_analyzes=create_order_data['remaining_of_analyzes'],
        price=create_order_data['price'],
        service_name=create_order_data['service_name'],
    )

    user_uuid = segmentation_analysis.order.user.uuid
    order_uuid = order.uuid
    analysis_uuid = segmentation_analysis.uuid

    url = resolve_url('service:analysis-read-update-delete', user_uuid, order_uuid, analysis_uuid)
    resp = client_api_auth.get(url)
    body = resp.json()

    assert resp.status_code == HTTPStatus.NOT_FOUND

    assert body['errors'] == ['Este usuário não possui este recurso cadastrado.']


def test_fail_read_using_another_user(client_api, second_user, segmentation_analysis):

    user_uuid = second_user.uuid
    order_uuid = segmentation_analysis.order.uuid
    analysis_uuid = segmentation_analysis.uuid

    url = resolve_url('service:analysis-read-update-delete', user_uuid, order_uuid, analysis_uuid)
    client_api.credentials(HTTP_AUTHORIZATION='Bearer ' + second_user.auth_token.key)
    resp = client_api.get(url)
    body = resp.json()

    assert resp.status_code == HTTPStatus.NOT_FOUND

    assert body['errors'] == ['Este usuário não possui este recurso cadastrado.']
