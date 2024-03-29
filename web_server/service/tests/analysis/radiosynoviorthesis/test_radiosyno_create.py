from copy import deepcopy
from decimal import Decimal
from http import HTTPStatus
from uuid import uuid4

import pytest
from dj_rest_auth.utils import jwt_encode
from django.shortcuts import resolve_url

from web_server.service.models import (
    FORMAT_DATE,
    ClinicDosimetryAnalysis,
    Order,
    PreClinicDosimetryAnalysis,
    RadiosynoAnalysis,
    SegmentationAnalysis,
)

# /api/v1/users/<uuid>/order/<uuid>/analysis/ - POST


def test_successfull(client_api_auth, radiosyno_order, form_data_radiosyno_analysis):
    """
    After analyses create order remaining of analyzes must be decreased by one
    """

    assert not ClinicDosimetryAnalysis.objects.exists()
    assert not PreClinicDosimetryAnalysis.objects.exists()
    assert not SegmentationAnalysis.objects.exists()
    assert not RadiosynoAnalysis.objects.exists()

    assert Order.objects.get(id=radiosyno_order.id).remaining_of_analyzes == radiosyno_order.remaining_of_analyzes

    url = resolve_url('service:analysis-list-create', radiosyno_order.user.uuid, radiosyno_order.uuid)
    resp = client_api_auth.post(url, data=form_data_radiosyno_analysis, format='multipart')
    body = resp.json()

    assert resp.status_code == HTTPStatus.CREATED

    assert not ClinicDosimetryAnalysis.objects.exists()
    assert not PreClinicDosimetryAnalysis.objects.exists()
    assert not SegmentationAnalysis.objects.exists()
    assert RadiosynoAnalysis.objects.exists()

    radiosyno_db = RadiosynoAnalysis.objects.first()

    expected = (
        f'/api/v1/users/{radiosyno_db.order.user.uuid}/orders/{radiosyno_db.order.uuid}/analysis/{radiosyno_db.uuid}/'
    )

    assert expected == resp.headers['Location']

    assert Order.objects.get(id=radiosyno_order.id).remaining_of_analyzes == radiosyno_order.remaining_of_analyzes - 1

    assert body['id'] == str(radiosyno_db.uuid)
    assert body['userId'] == str(radiosyno_db.order.user.uuid)
    assert body['orderId'] == str(radiosyno_db.order.uuid)
    assert body['status'] == radiosyno_db.get_status_display()
    assert body['active'] == radiosyno_db.active
    assert body['serviceName'] == radiosyno_db.order.get_service_name_display()
    assert body['createdAt'] == radiosyno_db.created_at.strftime(FORMAT_DATE)
    assert body['modifiedAt'] == radiosyno_db.modified_at.strftime(FORMAT_DATE)

    assert body['isotope'] == radiosyno_db.isotope.name

    # TODO: gerar a url completa
    assert body['imagesUrl'].startswith(f'http://testserver/media/{radiosyno_db.order.user.id}')

    assert body['report'] == ''


def test_fail_order_must_have_payment_confirmed(client_api_auth, radiosyno_order, form_data_radiosyno_analysis):

    radiosyno_order.status_payment = Order.PaymentStatus.AWAITING_PAYMENT
    radiosyno_order.save()

    assert not RadiosynoAnalysis.objects.exists()

    url = resolve_url('service:analysis-list-create', radiosyno_order.user.uuid, radiosyno_order.uuid)

    resp = client_api_auth.post(url, data=form_data_radiosyno_analysis, format='multipart')
    body = resp.json()

    assert resp.status_code == HTTPStatus.PAYMENT_REQUIRED

    assert not RadiosynoAnalysis.objects.exists()

    assert ['O pagamento deste pedido não foi confirmado.'] == body['errors']


def test_fail_analisys_name_must_be_unique_per_order(
    client_api_auth,
    user,
    form_data_radiosyno_analysis,
    radiosyno_analysis_info,
    radiosyno_analysis_file,
):
    """
    The analysis name must be unique in an order
    """

    order = radiosyno_analysis_info['order']

    images = deepcopy(radiosyno_analysis_file['images'])

    RadiosynoAnalysis.objects.create(**radiosyno_analysis_info, **radiosyno_analysis_file)

    assert RadiosynoAnalysis.objects.count() == 1

    form_data_radiosyno_analysis['images'] = images

    url = resolve_url('service:analysis-list-create', user.uuid, order.uuid)
    resp = client_api_auth.post(url, data=form_data_radiosyno_analysis, format='multipart')
    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    assert RadiosynoAnalysis.objects.count() == 1

    assert body['errors'] == ['Análise de Radiosinoviortese com este Order e Nome da análise já existe.']


def test_fail_not_have_remaining_of_analyzes(client_api_auth, user, form_data_radiosyno_analysis):
    """
    All requests for quotas have already been used in use
    """

    order = Order.objects.create(
        user=user,
        quantity_of_analyzes=3,
        price=Decimal('3000.00'),
        service_name=Order.ServicesName.RADIOSYNOVIORTHESIS.value,
        status_payment=Order.PaymentStatus.CONFIRMED,
        active=True,
    )

    order.remaining_of_analyzes = 0
    order.save()

    url = resolve_url('service:analysis-list-create', user.uuid, order.uuid)
    resp = client_api_auth.post(url, data=form_data_radiosyno_analysis, format='multipart')
    body = resp.json()

    assert resp.status_code == HTTPStatus.CONFLICT

    assert not RadiosynoAnalysis.objects.exists()

    assert body['errors'] == ['Todas as análises deste pedido já foram usadas.']


def test_fail_wrong_(client_api_auth, radiosyno_order, form_data_radiosyno_analysis):

    assert not RadiosynoAnalysis.objects.exists()

    url = resolve_url('service:analysis-list-create', radiosyno_order.user.uuid, uuid4())

    resp = client_api_auth.post(url, data=form_data_radiosyno_analysis, format='multipart')

    assert resp.status_code == HTTPStatus.NOT_FOUND

    assert not RadiosynoAnalysis.objects.exists()


def test_fail_with_order_from_another_user(
    client_api,
    user,
    second_user,
    tree_orders_of_two_diff_users,
    form_data_radiosyno_analysis,
):
    """
    User mut be create analysis only in your own orders
    """

    order_first_user = Order.objects.filter(user=user).first()

    url = resolve_url('service:analysis-list-create', second_user.uuid, order_first_user.uuid)

    access_token, _ = jwt_encode(second_user)
    client_api.cookies.load({'jwt-access-token': access_token})
    resp = client_api.post(url, data=form_data_radiosyno_analysis, format='multipart')

    assert resp.status_code == HTTPStatus.NOT_FOUND

    assert not RadiosynoAnalysis.objects.exists()


@pytest.mark.parametrize(
    'field, error',
    [
        ('images', ['images: Este campo é obrigatório.']),
        ('analysisName', ['analysis_name: Este campo é obrigatório.']),
        ('isotope', ['isotope: Este campo é obrigatório.']),
    ],
)
def test_fail_missing_fields(field, error, client_api_auth, radiosyno_order, form_data_radiosyno_analysis):

    form_data_radiosyno_analysis.pop(field)

    url = resolve_url('service:analysis-list-create', radiosyno_order.user.uuid, radiosyno_order.uuid)

    resp = client_api_auth.post(url, data=form_data_radiosyno_analysis, format='multipart')

    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    assert not RadiosynoAnalysis.objects.exists()

    assert body['errors'] == error


@pytest.mark.parametrize(
    'field, value, error',
    [
        (
            'analysisName',
            'ss',
            ['analysis_name: Certifique-se de que o valor tenha no mínimo 3 caracteres (ele possui 2).'],
        ),
        (
            'isotope',
            'ss',
            ['isotope: Isótopo não registrado.'],
        ),
    ],
)
def test_fail_invalid_fields(field, value, error, client_api_auth, radiosyno_order, form_data_radiosyno_analysis):

    form_data_radiosyno_analysis[field] = value

    url = resolve_url('service:analysis-list-create', radiosyno_order.user.uuid, radiosyno_order.uuid)
    resp = client_api_auth.post(url, data=form_data_radiosyno_analysis, format='multipart')
    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    assert not RadiosynoAnalysis.objects.exists()

    assert body['errors'] == error
