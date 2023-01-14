from http import HTTPStatus
from uuid import uuid4

from dj_rest_auth.utils import jwt_encode
from django.shortcuts import resolve_url

from web_server.service.models import Order, RadiosynoAnalysis

# /api/v1/users/<uuid>/order/<uuid>/analysis/<uuid> - DELETE


def test_successfull(client_api_auth, radiosyno_analysis_update_or_del_is_possible):

    user_uuid = radiosyno_analysis_update_or_del_is_possible.order.user.uuid
    order_uuid = radiosyno_analysis_update_or_del_is_possible.order.uuid
    analysis_uuid = radiosyno_analysis_update_or_del_is_possible.uuid

    order = Order.objects.get(uuid=order_uuid)

    remaining_of_analyzes = order.remaining_of_analyzes

    assert RadiosynoAnalysis.objects.exists()

    url = resolve_url('service:analysis-read-update-delete', user_uuid, order_uuid, analysis_uuid)
    resp = client_api_auth.delete(url)

    body = resp.json()

    assert resp.status_code == HTTPStatus.OK

    update_order = Order.objects.get(uuid=order_uuid)
    assert update_order.remaining_of_analyzes == remaining_of_analyzes + 1

    assert not RadiosynoAnalysis.objects.exists()

    assert body == {'id': str(analysis_uuid), 'message': 'Análise excluída com sucesso!'}


def test_fail_successfull_invalid_status(client_api_auth, radiosyno_analysis):
    """
    The analysis must have INVALID_INFOS status
    """

    user_uuid = radiosyno_analysis.order.user.uuid
    order_uuid = radiosyno_analysis.order.uuid
    analysis_uuid = radiosyno_analysis.uuid

    order = Order.objects.get(uuid=order_uuid)

    remaining_of_analyzes = order.remaining_of_analyzes

    assert RadiosynoAnalysis.objects.exists()

    url = resolve_url('service:analysis-read-update-delete', user_uuid, order_uuid, analysis_uuid)
    resp = client_api_auth.delete(url)

    body = resp.json()

    assert resp.status_code == HTTPStatus.CONFLICT

    update_order = Order.objects.get(uuid=order_uuid)
    assert update_order.remaining_of_analyzes == remaining_of_analyzes

    assert RadiosynoAnalysis.objects.exists()

    expected = [
        'Não foi possível excluir/atualizar esta análise.'
        ' Somente análises com o status Informações inválidas ou Dados enviados podem ser excluidas.'
    ]

    assert expected == body['errors']


def test_fail_wrong_analysis_id(client_api_auth, radiosyno_analysis):

    user_uuid = radiosyno_analysis.order.user.uuid
    order_uuid = radiosyno_analysis.order.uuid
    analysis_uuid = uuid4()

    assert RadiosynoAnalysis.objects.exists()

    url = resolve_url('service:analysis-read-update-delete', user_uuid, order_uuid, analysis_uuid)
    resp = client_api_auth.delete(url)
    body = resp.json()

    assert resp.status_code == HTTPStatus.NOT_FOUND

    assert RadiosynoAnalysis.objects.exists()

    assert body['errors'] == ['Este usuário não possui este recurso cadastrado.']


def test_fail_using_another_order(client_api_auth, user, radiosyno_analysis, create_order_data):

    order = Order.objects.create(
        user=user,
        quantity_of_analyzes=create_order_data['quantity_of_analyzes'],
        remaining_of_analyzes=create_order_data['remaining_of_analyzes'],
        price=create_order_data['price'],
        service_name=create_order_data['service_name'],
    )

    assert RadiosynoAnalysis.objects.exists()

    user_uuid = radiosyno_analysis.order.user.uuid
    order_uuid = order.uuid
    analysis_uuid = radiosyno_analysis.uuid

    url = resolve_url('service:analysis-read-update-delete', user_uuid, order_uuid, analysis_uuid)
    resp = client_api_auth.delete(url)
    body = resp.json()

    assert RadiosynoAnalysis.objects.exists()

    assert resp.status_code == HTTPStatus.NOT_FOUND

    assert body['errors'] == ['Este usuário não possui este recurso cadastrado.']


def test_fail_using_another_user(client_api, second_user, radiosyno_analysis):

    user_uuid = second_user.uuid
    order_uuid = radiosyno_analysis.order.uuid
    analysis_uuid = radiosyno_analysis.uuid

    url = resolve_url('service:analysis-read-update-delete', user_uuid, order_uuid, analysis_uuid)
    access_token, _ = jwt_encode(second_user)
    client_api.cookies.load({'jwt-access-token': access_token})
    resp = client_api.delete(url)
    body = resp.json()

    assert resp.status_code == HTTPStatus.NOT_FOUND

    assert body['errors'] == ['Este usuário não possui este recurso cadastrado.']
