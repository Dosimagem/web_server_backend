from http import HTTPStatus
from uuid import uuid4

from django.shortcuts import resolve_url

from web_server.service.models import Order, PreClinicDosimetryAnalysis

# /api/v1/users/<uuid>/order/<uuid>/analysis/<uuid> - DELETE


def test_successfull(client_api_auth, preclinic_dosi_update_del_is_possible):

    user_uuid = preclinic_dosi_update_del_is_possible.order.user.uuid
    order_uuid = preclinic_dosi_update_del_is_possible.order.uuid
    analysis_uuid = preclinic_dosi_update_del_is_possible.uuid

    order = Order.objects.get(uuid=order_uuid)

    remaining_of_analyzes = order.remaining_of_analyzes

    assert PreClinicDosimetryAnalysis.objects.exists()

    url = resolve_url(
        'service:analysis-read-update-delete',
        user_uuid,
        order_uuid,
        analysis_uuid,
    )
    resp = client_api_auth.delete(url)

    body = resp.json()

    assert resp.status_code == HTTPStatus.OK

    update_order = Order.objects.get(uuid=order_uuid)
    assert update_order.remaining_of_analyzes == remaining_of_analyzes + 1

    assert not PreClinicDosimetryAnalysis.objects.exists()

    assert body == {'id': str(analysis_uuid), 'message': 'Análise deletada com sucesso!'}


def test_fail_successfull_invalid_status(client_api_auth, preclinic_dosimetry):
    """
    The analysis must have INVALID_INFOS or DATA_SENT status
    """

    user_uuid = preclinic_dosimetry.order.user.uuid
    order_uuid = preclinic_dosimetry.order.uuid
    analysis_uuid = preclinic_dosimetry.uuid

    order = Order.objects.get(uuid=order_uuid)

    remaining_of_analyzes = order.remaining_of_analyzes

    assert PreClinicDosimetryAnalysis.objects.exists()

    url = resolve_url('service:analysis-read-update-delete', user_uuid, order_uuid, analysis_uuid)
    resp = client_api_auth.delete(url)

    body = resp.json()

    assert resp.status_code == HTTPStatus.CONFLICT

    update_order = Order.objects.get(uuid=order_uuid)
    assert update_order.remaining_of_analyzes == remaining_of_analyzes

    assert PreClinicDosimetryAnalysis.objects.exists()

    expected = [
        'Não foi possivel deletar/atualizar essa análise.'
        ' Apenas análises com os status Informações inválidas ou Dados enviados podem ser deletadas'
    ]

    assert expected == body['errors']


def test_fail_wrong_analysis_id(client_api_auth, preclinic_dosimetry):

    user_uuid = preclinic_dosimetry.order.user.uuid
    order_uuid = preclinic_dosimetry.order.uuid
    analysis_uuid = uuid4()

    assert PreClinicDosimetryAnalysis.objects.exists()

    url = resolve_url('service:analysis-read-update-delete', user_uuid, order_uuid, analysis_uuid)
    resp = client_api_auth.delete(url)
    body = resp.json()

    assert resp.status_code == HTTPStatus.NOT_FOUND

    assert PreClinicDosimetryAnalysis.objects.exists()

    assert body['errors'] == ['Este usuário não possui este recurso cadastrado.']


def test_fail_using_another_order(client_api_auth, user, preclinic_dosimetry, create_order_data):

    order = Order.objects.create(
        user=user,
        quantity_of_analyzes=create_order_data['quantity_of_analyzes'],
        remaining_of_analyzes=create_order_data['remaining_of_analyzes'],
        price=create_order_data['price'],
        service_name=create_order_data['service_name'],
    )

    assert PreClinicDosimetryAnalysis.objects.exists()

    user_uuid = preclinic_dosimetry.order.user.uuid
    order_uuid = order.uuid
    analysis_uuid = preclinic_dosimetry.uuid

    url = resolve_url(
        'service:analysis-read-update-delete',
        user_uuid,
        order_uuid,
        analysis_uuid,
    )
    resp = client_api_auth.delete(url)
    body = resp.json()

    assert PreClinicDosimetryAnalysis.objects.exists()

    assert resp.status_code == HTTPStatus.NOT_FOUND

    assert body['errors'] == ['Este usuário não possui este recurso cadastrado.']


def test_fail_using_another_user(client_api, second_user, preclinic_dosimetry):

    user_uuid = second_user.uuid
    order_uuid = preclinic_dosimetry.order.uuid
    analysis_uuid = preclinic_dosimetry.uuid

    url = resolve_url(
        'service:analysis-read-update-delete',
        user_uuid,
        order_uuid,
        analysis_uuid,
    )
    client_api.credentials(HTTP_AUTHORIZATION='Bearer ' + second_user.auth_token.key)
    resp = client_api.delete(url)
    body = resp.json()

    assert resp.status_code == HTTPStatus.NOT_FOUND

    assert body['errors'] == ['Este usuário não possui este recurso cadastrado.']
