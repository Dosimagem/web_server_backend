from decimal import Decimal
from http import HTTPStatus
from uuid import uuid4

import pytest
from django.core.files.base import ContentFile
from django.shortcuts import resolve_url

from web_server.service.models import Order, RadiosynoAnalysis


@pytest.fixture
def update_form_data(lu_177):
    return {'analysisName': 'New analsysis name', 'isotope': lu_177.name}


def _verified_unchanged_information_db(analysis):

    analysis_db = RadiosynoAnalysis.objects.get(id=analysis.id)

    assert analysis_db.analysis_name == analysis.analysis_name
    assert analysis_db.isotope.name == analysis.isotope.name
    assert analysis_db.images.file.read() == analysis.images.file.read()


# /api/v1/users/<uuid>/order/<uuid>/analysis/<uuid> - PUT


def test_successfull(client_api_auth, radiosyno_analysis_update_or_del_is_possible, update_form_data):

    update_form_data['images'] = ContentFile(b'New File Update', name='images.zip')

    user_uuid = radiosyno_analysis_update_or_del_is_possible.order.user.uuid
    order_uuid = radiosyno_analysis_update_or_del_is_possible.order.uuid
    analysis_uuid = radiosyno_analysis_update_or_del_is_possible.uuid

    url = resolve_url('service:analysis-read-update-delete', user_uuid, order_uuid, analysis_uuid)
    resp = client_api_auth.put(url, data=update_form_data, format='multipart')

    assert resp.status_code == HTTPStatus.NO_CONTENT

    analysis_db = RadiosynoAnalysis.objects.get(id=radiosyno_analysis_update_or_del_is_possible.id)

    assert analysis_db.analysis_name == update_form_data['analysisName']
    assert analysis_db.isotope.name == update_form_data['isotope']
    assert analysis_db.images.file.read() == b'New File Update'
    assert analysis_db.status == RadiosynoAnalysis.Status.DATA_SENT


def test_optional_images_successfull(client_api_auth, radiosyno_analysis_update_or_del_is_possible, update_form_data):

    user_uuid = radiosyno_analysis_update_or_del_is_possible.order.user.uuid
    order_uuid = radiosyno_analysis_update_or_del_is_possible.order.uuid
    analysis_uuid = radiosyno_analysis_update_or_del_is_possible.uuid

    url = resolve_url('service:analysis-read-update-delete', user_uuid, order_uuid, analysis_uuid)
    resp = client_api_auth.put(url, data=update_form_data, format='multipart')

    assert resp.status_code == HTTPStatus.NO_CONTENT

    analysis_db = RadiosynoAnalysis.objects.get(id=radiosyno_analysis_update_or_del_is_possible.id)

    assert analysis_db.analysis_name == update_form_data['analysisName']
    assert analysis_db.isotope.name == update_form_data['isotope']
    assert analysis_db.images.file.read() == radiosyno_analysis_update_or_del_is_possible.images.file.read()
    assert analysis_db.status == RadiosynoAnalysis.Status.DATA_SENT


def test_fail_successfull_invalid_status(client_api_auth, radiosyno_analysis, update_form_data):
    """
    The analysis must have INVALID_INFOS status
    """

    user_uuid = radiosyno_analysis.order.user.uuid
    order_uuid = radiosyno_analysis.order.uuid
    analysis_uuid = radiosyno_analysis.uuid

    url = resolve_url('service:analysis-read-update-delete', user_uuid, order_uuid, analysis_uuid)
    resp = client_api_auth.put(url, data=update_form_data, format='multipart')
    body = resp.json()

    assert resp.status_code == HTTPStatus.CONFLICT

    expected = [
        'Não foi possivel deletar/atualizar essa análise.'
        ' Apenas análises com os status Informações inválidas ou Dados enviados podem ser deletadas'
    ]

    assert expected == body['errors']

    _verified_unchanged_information_db(radiosyno_analysis)


def test_fail_wrong_analysis_id(client_api_auth, radiosyno_analysis_update_or_del_is_possible, update_form_data):

    user_uuid = radiosyno_analysis_update_or_del_is_possible.order.user.uuid
    order_uuid = radiosyno_analysis_update_or_del_is_possible.order.uuid
    analysis_uuid = uuid4()

    url = resolve_url('service:analysis-read-update-delete', user_uuid, order_uuid, analysis_uuid)
    resp = client_api_auth.put(url, data=update_form_data, format='multipart')
    body = resp.json()

    assert resp.status_code == HTTPStatus.NOT_FOUND
    assert body['errors'] == ['Este usuário não possui este recurso cadastrado.']

    _verified_unchanged_information_db(radiosyno_analysis_update_or_del_is_possible)


def test_fail_wrong_another_order(
    client_api_auth, user, radiosyno_analysis_update_or_del_is_possible, update_form_data
):

    order = Order.objects.create(
        user=user,
        quantity_of_analyzes=10,
        remaining_of_analyzes=10,
        price=Decimal('1000.00'),
        service_name=Order.ServicesName.RADIOSYNOVIORTHESIS.value,
    )

    user_uuid = radiosyno_analysis_update_or_del_is_possible.order.user.uuid
    order_uuid = order.uuid
    analysis_uuid = radiosyno_analysis_update_or_del_is_possible.uuid

    url = resolve_url('service:analysis-read-update-delete', user_uuid, order_uuid, analysis_uuid)
    resp = client_api_auth.put(url, data=update_form_data, format='multipart')
    body = resp.json()

    assert resp.status_code == HTTPStatus.NOT_FOUND
    assert body['errors'] == ['Este usuário não possui este recurso cadastrado.']

    _verified_unchanged_information_db(radiosyno_analysis_update_or_del_is_possible)


def test_fail_wrong_another_user(
    client_api,
    second_user,
    radiosyno_analysis_update_or_del_is_possible,
    update_form_data,
):

    user_uuid = second_user.uuid
    order_uuid = radiosyno_analysis_update_or_del_is_possible.order.uuid
    analysis_uuid = radiosyno_analysis_update_or_del_is_possible.uuid

    url = resolve_url('service:analysis-read-update-delete', user_uuid, order_uuid, analysis_uuid)
    client_api.credentials(HTTP_AUTHORIZATION='Bearer ' + second_user.auth_token.key)
    resp = client_api.put(url, data=update_form_data, format='multipart')
    body = resp.json()

    assert resp.status_code == HTTPStatus.NOT_FOUND
    assert body['errors'] == ['Este usuário não possui este recurso cadastrado.']

    _verified_unchanged_information_db(radiosyno_analysis_update_or_del_is_possible)


@pytest.mark.parametrize(
    'field, error',
    [
        ('analysisName', ['O campo nome da análise é obrigatório.']),
        ('isotope', ['O campo isotopo é obrigatório.']),
    ],
)
def test_fail_missing_fields(
    field, error, client_api_auth, radiosyno_analysis_update_or_del_is_possible, update_form_data
):

    update_form_data.pop(field)

    user_uuid = radiosyno_analysis_update_or_del_is_possible.order.user.uuid
    order_uuid = radiosyno_analysis_update_or_del_is_possible.order.uuid
    analysis_uuid = radiosyno_analysis_update_or_del_is_possible.uuid

    url = resolve_url('service:analysis-read-update-delete', user_uuid, order_uuid, analysis_uuid)

    resp = client_api_auth.put(url, data=update_form_data, format='multipart')

    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    assert body['errors'] == error

    _verified_unchanged_information_db(radiosyno_analysis_update_or_del_is_possible)


@pytest.mark.parametrize(
    'field, value, error',
    [
        ('isotope', 'll-12', ['Isotopo não registrado.']),
    ],
)
def test_fail_invalid_fields(
    field, value, error, client_api_auth, radiosyno_analysis_update_or_del_is_possible, update_form_data
):

    update_form_data[field] = value

    user_uuid = radiosyno_analysis_update_or_del_is_possible.order.user.uuid
    order_uuid = radiosyno_analysis_update_or_del_is_possible.order.uuid
    analysis_uuid = radiosyno_analysis_update_or_del_is_possible.uuid

    url = resolve_url('service:analysis-read-update-delete', user_uuid, order_uuid, analysis_uuid)

    resp = client_api_auth.put(url, data=update_form_data, format='multipart')

    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    assert body['errors'] == error

    _verified_unchanged_information_db(radiosyno_analysis_update_or_del_is_possible)


def test_fail_analysis_name_must_be_unique(
    client_api_auth,
    radiosyno_order,
    radiosyno_analysis_update_or_del_is_possible,
    lu_177,
):

    other_analysis = RadiosynoAnalysis.objects.create(
        order=radiosyno_order,
        analysis_name='Analysis 2',
        isotope=lu_177,
        images=ContentFile(b'CT e SPET files 1', name='images.zip'),
    )

    update_form_data = {}
    update_form_data['analysisName'] = other_analysis.analysis_name
    update_form_data['isotope'] = 'Lu-177'

    user_uuid = radiosyno_analysis_update_or_del_is_possible.order.user.uuid
    order_uuid = radiosyno_analysis_update_or_del_is_possible.order.uuid
    analysis_uuid = radiosyno_analysis_update_or_del_is_possible.uuid

    url = resolve_url('service:analysis-read-update-delete', user_uuid, order_uuid, analysis_uuid)

    resp = client_api_auth.put(url, data=update_form_data, format='multipart')

    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    assert body['errors'] == ['Análises com esse nome já existe para esse pedido.']

    _verified_unchanged_information_db(radiosyno_analysis_update_or_del_is_possible)
