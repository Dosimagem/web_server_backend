from http import HTTPStatus
from uuid import uuid4

from django.shortcuts import resolve_url

from web_server.service.models import ClinicDosimetryAnalysis, Order


def test_delete_clinic_dosimetry_successfull(client_api_auth, clinic_dosimetry_update_delete):
    '''
    /api/v1/users/<uuid>/order/<uuid>/analysis/<uuid> - DELETE
    '''

    user_uuid = clinic_dosimetry_update_delete.user.uuid
    order_uuid = clinic_dosimetry_update_delete.order.uuid
    analysis_uuid = clinic_dosimetry_update_delete.uuid

    order = Order.objects.get(uuid=order_uuid)

    remaining_of_analyzes = order.remaining_of_analyzes

    assert ClinicDosimetryAnalysis.objects.exists()

    url = resolve_url('api:analysis-read-update-delete', user_uuid, order_uuid, analysis_uuid)
    resp = client_api_auth.delete(url)

    body = resp.json()

    assert resp.status_code == HTTPStatus.OK

    update_order = Order.objects.get(uuid=order_uuid)
    assert update_order.remaining_of_analyzes == remaining_of_analyzes + 1

    assert not ClinicDosimetryAnalysis.objects.exists()

    assert body == {'id': str(analysis_uuid), 'message': 'Análise deletada com sucesso!'}


def test_fail_delete_clinic_dosimetry_successfull_invalid_status(client_api_auth, clinic_dosimetry):
    '''
    /api/v1/users/<uuid>/order/<uuid>/analysis/<uuid> - DELETE
    The analysis must have INVALID_INFOS status
    '''

    user_uuid = clinic_dosimetry.user.uuid
    order_uuid = clinic_dosimetry.order.uuid
    analysis_uuid = clinic_dosimetry.uuid

    order = Order.objects.get(uuid=order_uuid)

    remaining_of_analyzes = order.remaining_of_analyzes

    assert ClinicDosimetryAnalysis.objects.exists()

    url = resolve_url('api:analysis-read-update-delete', user_uuid, order_uuid, analysis_uuid)
    resp = client_api_auth.delete(url)

    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    update_order = Order.objects.get(uuid=order_uuid)
    assert update_order.remaining_of_analyzes == remaining_of_analyzes

    assert ClinicDosimetryAnalysis.objects.exists()

    assert body == {'errors': 'Não foi possivel deletar essa análise.'}


def test_fail_delete_clinic_dosimetry_wrong_analysis_id(client_api_auth, clinic_dosimetry):
    '''
    /api/v1/users/<uuid>/order/<uuid>/analysis/<uuid> - DELETE
    '''

    user_uuid = clinic_dosimetry.user.uuid
    order_uuid = clinic_dosimetry.order.uuid
    analysis_uuid = uuid4()

    assert ClinicDosimetryAnalysis.objects.exists()

    url = resolve_url('api:analysis-read-update-delete', user_uuid, order_uuid, analysis_uuid)
    resp = client_api_auth.delete(url)
    body = resp.json()

    assert resp.status_code == HTTPStatus.NOT_FOUND

    assert ClinicDosimetryAnalysis.objects.exists()

    assert body['errors'] == ['Este usuário não possui este recurso cadastrado.']


def test_fail_delete_clinic_dosimetry_using_another_order(client_api_auth, user, clinic_dosimetry, create_order_data):
    '''
    /api/v1/users/<uuid>/order/<uuid>/analysis/<uuid> - DELETE
    '''
    order = Order.objects.create(user=user,
                                 quantity_of_analyzes=create_order_data['quantity_of_analyzes'],
                                 remaining_of_analyzes=create_order_data['remaining_of_analyzes'],
                                 price=create_order_data['price'],
                                 service_name=create_order_data['service_name']
                                 )

    assert ClinicDosimetryAnalysis.objects.exists()

    user_uuid = clinic_dosimetry.user.uuid
    order_uuid = order.uuid
    analysis_uuid = clinic_dosimetry.uuid

    url = resolve_url('api:analysis-read-update-delete', user_uuid, order_uuid, analysis_uuid)
    resp = client_api_auth.delete(url)
    body = resp.json()

    assert ClinicDosimetryAnalysis.objects.exists()

    assert resp.status_code == HTTPStatus.NOT_FOUND

    assert body['errors'] == ['Este usuário não possui este recurso cadastrado.']


def test_fail_delete_clinic_dosimetry_using_another_user(client_api, second_user, clinic_dosimetry):
    '''
    /api/v1/users/<uuid>/order/<uuid>/analysis/<uuid> - DELETE
    '''

    user_uuid = second_user.uuid
    order_uuid = clinic_dosimetry.order.uuid
    analysis_uuid = clinic_dosimetry.uuid

    url = resolve_url('api:analysis-read-update-delete', user_uuid, order_uuid, analysis_uuid)
    client_api.credentials(HTTP_AUTHORIZATION='Bearer ' + second_user.auth_token.key)
    resp = client_api.delete(url)
    body = resp.json()

    assert resp.status_code == HTTPStatus.NOT_FOUND

    assert body['errors'] == ['Este usuário não possui este recurso cadastrado.']
