from http import HTTPStatus
from uuid import uuid4

from django.shortcuts import resolve_url
from dj_rest_auth.utils import jwt_encode

from web_server.service.models import FORMAT_DATE, ClinicDosimetryAnalysis, Order

# /api/v1/users/<uuid>/order/<uuid>/analysis/<uuid> - GET


def test_successfull(client_api_auth, clinic_dosimetry):
    """
    /api/v1/users/<uuid>/order/<uuid>/analysis/<uuid> - GET
    """

    user = clinic_dosimetry.order.user
    order = clinic_dosimetry.order

    url = resolve_url('service:analysis-read-update-delete', user.uuid, order.uuid, clinic_dosimetry.uuid)
    resp = client_api_auth.get(url)
    analysis_db = ClinicDosimetryAnalysis.objects.get(id=clinic_dosimetry.id)

    assert resp.status_code == HTTPStatus.OK

    body = resp.json()

    assert body['id'] == str(analysis_db.uuid)
    assert body['userId'] == str(analysis_db.order.user.uuid)
    assert body['orderId'] == str(analysis_db.order.uuid)
    assert body['calibrationId'] == str(analysis_db.calibration.uuid)
    assert body['status'] == analysis_db.get_status_display()
    assert body['active'] == analysis_db.active
    assert body['serviceName'] == analysis_db.order.get_service_name_display()
    assert body['createdAt'] == analysis_db.created_at.strftime(FORMAT_DATE)
    assert body['modifiedAt'] == analysis_db.modified_at.strftime(FORMAT_DATE)

    assert body['injectedActivity'] == analysis_db.injected_activity
    assert body['analysisName'] == analysis_db.analysis_name
    assert body['administrationDatetime'] == analysis_db.administration_datetime.strftime(FORMAT_DATE)

    # TODO: Pensar uma forma melhor
    assert body['imagesUrl'].startswith(f'http://testserver/media/{analysis_db.order.user.id}')

    assert body['report'] == ''


def test_fail_wrong_analysis_id(client_api_auth, clinic_dosimetry):

    user_uuid = clinic_dosimetry.order.user.uuid
    order_uuid = clinic_dosimetry.order.uuid
    analysis_uuid = uuid4()

    url = resolve_url('service:analysis-read-update-delete', user_uuid, order_uuid, analysis_uuid)
    resp = client_api_auth.get(url)
    body = resp.json()

    assert resp.status_code == HTTPStatus.NOT_FOUND

    assert body['errors'] == ['Este usuário não possui este recurso cadastrado.']


def test_fail_using_another_order(client_api_auth, user, clinic_dosimetry, create_order_data):

    order = Order.objects.create(
        user=user,
        quantity_of_analyzes=create_order_data['quantity_of_analyzes'],
        remaining_of_analyzes=create_order_data['remaining_of_analyzes'],
        price=create_order_data['price'],
        service_name=create_order_data['service_name'],
    )

    user_uuid = clinic_dosimetry.order.user.uuid
    order_uuid = order.uuid
    analysis_uuid = clinic_dosimetry.uuid

    url = resolve_url(
        'service:analysis-read-update-delete',
        user_uuid,
        order_uuid,
        analysis_uuid,
    )
    resp = client_api_auth.get(url)
    body = resp.json()

    assert resp.status_code == HTTPStatus.NOT_FOUND

    assert body['errors'] == ['Este usuário não possui este recurso cadastrado.']


def test_fail_using_another_user(client_api, second_user, clinic_dosimetry):

    user_uuid = second_user.uuid
    order_uuid = clinic_dosimetry.order.uuid
    analysis_uuid = clinic_dosimetry.uuid

    url = resolve_url('service:analysis-read-update-delete', user_uuid, order_uuid, analysis_uuid)

    access_token, _ = jwt_encode(second_user)
    client_api.cookies.load({'jwt-access-token': access_token})

    resp = client_api.get(url)
    body = resp.json()

    assert resp.status_code == HTTPStatus.NOT_FOUND

    assert body['errors'] == ['Este usuário não possui este recurso cadastrado.']


def test_error_message_only_status_invalid_info(client_api_auth, clinic_dosimetry):

    clinic_dosimetry.message_to_user = 'Arquivos CT faltando.'
    clinic_dosimetry.save()

    user = clinic_dosimetry.order.user
    order = clinic_dosimetry.order

    url = resolve_url('service:analysis-read-update-delete', user.uuid, order.uuid, clinic_dosimetry.uuid)
    resp = client_api_auth.get(url)

    body = resp.json()

    assert body['messageToUser'] == ''

    clinic_dosimetry.status = ClinicDosimetryAnalysis.Status.INVALID_INFOS
    clinic_dosimetry.save()

    url = resolve_url('service:analysis-read-update-delete', user.uuid, order.uuid, clinic_dosimetry.uuid)
    resp = client_api_auth.get(url)

    body = resp.json()

    assert body['messageToUser'] == 'Arquivos CT faltando.'
