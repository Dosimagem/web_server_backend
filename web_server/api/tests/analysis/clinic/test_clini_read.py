from http import HTTPStatus
from uuid import uuid4

from django.shortcuts import resolve_url

from web_server.service.models import ClinicDosimetryAnalysis, FORMAT_DATE, Order


def test_read_clinic_dosimetry_successfull(client_api_auth, clinic_dosimetry):
    '''
    /api/v1/users/<uuid>/order/<uuid>/analysis/<uuid> - GET
    '''

    user = clinic_dosimetry.user
    order = clinic_dosimetry.order

    url = resolve_url('api:analysis-read-update-delete', user.uuid, order.uuid, clinic_dosimetry.uuid)
    resp = client_api_auth.get(url)
    analysis_db = ClinicDosimetryAnalysis.objects.get(id=clinic_dosimetry.id)

    assert resp.status_code == HTTPStatus.OK

    body = resp.json()

    assert body['id'] == str(analysis_db.uuid)
    assert body['userId'] == str(analysis_db.user.uuid)
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
    assert body['imagesUrl'].startswith(
        f'http://testserver/media/{analysis_db.user.id}/clinic_dosimetry'
        )

    assert body['report'] == ''


def test_fail_read_clinic_dosimetry_wrong_analysis_id(client_api_auth, clinic_dosimetry):
    '''
    /api/v1/users/<uuid>/order/<uuid>/analysis/<uuid> - GET
    '''

    user_uuid = clinic_dosimetry.user.uuid
    order_uuid = clinic_dosimetry.order.uuid
    analysis_uuid = uuid4()

    url = resolve_url('api:analysis-read-update-delete', user_uuid, order_uuid, analysis_uuid)
    resp = client_api_auth.get(url)
    body = resp.json()

    assert resp.status_code == HTTPStatus.NOT_FOUND

    assert body['errors'] == ['Este usuário não possui este recurso cadastrado.']


def test_fail_read_clinic_dosimetry_using_another_order(client_api_auth, user, clinic_dosimetry, create_order_data):
    '''
    /api/v1/users/<uuid>/order/<uuid>/analysis/<uuid> - GET
    '''
    order = Order.objects.create(user=user,
                                 quantity_of_analyzes=create_order_data['quantity_of_analyzes'],
                                 remaining_of_analyzes=create_order_data['remaining_of_analyzes'],
                                 price=create_order_data['price'],
                                 service_name=create_order_data['service_name']
                                 )

    user_uuid = clinic_dosimetry.user.uuid
    order_uuid = order.uuid
    analysis_uuid = clinic_dosimetry.uuid

    url = resolve_url('api:analysis-read-update-delete', user_uuid, order_uuid, analysis_uuid)
    resp = client_api_auth.get(url)
    body = resp.json()

    assert resp.status_code == HTTPStatus.NOT_FOUND

    assert body['errors'] == ['Este usuário não possui este recurso cadastrado.']


def test_fail_read_clinic_dosimetry_using_another_user(client_api, second_user, clinic_dosimetry):
    '''
    /api/v1/users/<uuid>/order/<uuid>/analysis/<uuid> - GET
    '''

    user_uuid = second_user.uuid
    order_uuid = clinic_dosimetry.order.uuid
    analysis_uuid = clinic_dosimetry.uuid

    url = resolve_url('api:analysis-read-update-delete', user_uuid, order_uuid, analysis_uuid)
    client_api.credentials(HTTP_AUTHORIZATION='Bearer ' + second_user.auth_token.key)
    resp = client_api.get(url)
    body = resp.json()

    assert resp.status_code == HTTPStatus.NOT_FOUND

    assert body['errors'] == ['Este usuário não possui este recurso cadastrado.']
