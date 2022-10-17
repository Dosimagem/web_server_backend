from copy import deepcopy
from decimal import Decimal
from http import HTTPStatus
from uuid import uuid4

import pytest
from django.shortcuts import resolve_url

from web_server.service.models import (
    FORMAT_DATE,
    ClinicDosimetryAnalysis,
    Order,
    PreClinicDosimetryAnalysis,
    SegmentationAnalysis,
)

# /api/v1/users/<uuid>/order/<uuid>/analysis/ - POST


def test_successful(client_api_auth, segmentation_order, form_data_segmentation_analysis):
    """
    After analyses create order remaining of analyzes must be decreased by one
    """

    assert not ClinicDosimetryAnalysis.objects.exists()
    assert not PreClinicDosimetryAnalysis.objects.exists()
    assert not SegmentationAnalysis.objects.exists()

    order = segmentation_order

    assert Order.objects.get(id=order.id).remaining_of_analyzes == order.remaining_of_analyzes

    url = resolve_url('service:analysis-list-create', order.user.uuid, order.uuid)
    resp = client_api_auth.post(url, data=form_data_segmentation_analysis, format='multipart')
    body = resp.json()

    assert resp.status_code == HTTPStatus.CREATED

    assert not ClinicDosimetryAnalysis.objects.exists()
    assert not PreClinicDosimetryAnalysis.objects.exists()
    assert SegmentationAnalysis.objects.exists()

    analysis_db = SegmentationAnalysis.objects.first()

    assert Order.objects.get(id=order.id).remaining_of_analyzes == order.remaining_of_analyzes - 1

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


def test_fail_order_must_have_payment_confirmed(client_api_auth, segmentation_order, form_data_segmentation_analysis):

    segmentation_order.status_payment = Order.AWAITING_PAYMENT
    segmentation_order.save()

    assert not PreClinicDosimetryAnalysis.objects.exists()

    url = resolve_url('service:analysis-list-create', segmentation_order.user.uuid, segmentation_order.uuid)

    resp = client_api_auth.post(url, data=form_data_segmentation_analysis, format='multipart')
    body = resp.json()

    assert resp.status_code == HTTPStatus.CONFLICT

    assert not PreClinicDosimetryAnalysis.objects.exists()

    assert ['O pagamento desse pedido não foi confirmado.'] == body['errors']


def test_fail_analisys_name_must_be_unique_per_order(
    client_api_auth, form_data_segmentation_analysis, segmentation_analysis_info, segmentation_analysis_file
):
    """
    The analysis name must be unique in an order
    """

    order = segmentation_analysis_info['order']

    images = deepcopy(segmentation_analysis_file['images'])

    SegmentationAnalysis.objects.create(**segmentation_analysis_info, **segmentation_analysis_file)

    assert SegmentationAnalysis.objects.count() == 1

    form_data_segmentation_analysis['images'] = images

    url = resolve_url('service:analysis-list-create', order.user.uuid, order.uuid)
    resp = client_api_auth.post(url, data=form_data_segmentation_analysis, format='multipart')
    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    assert SegmentationAnalysis.objects.count() == 1

    assert body['errors'] == ['Análises com esse nome já existe para esse pedido.']


def test_fail_not_have_remaining_of_analyzes(client_api_auth, user, form_data_segmentation_analysis):
    """
    All requests for quotas have already been used in use
    """

    order = Order.objects.create(
        user=user,
        quantity_of_analyzes=3,
        remaining_of_analyzes=0,
        price=Decimal('3000.00'),
        service_name=Order.SEGMENTANTION_QUANTIFICATION,
        status_payment=Order.AWAITING_PAYMENT,
        permission=True,
    )

    url = resolve_url('service:analysis-list-create', user.uuid, order.uuid)
    resp = client_api_auth.post(url, data=form_data_segmentation_analysis, format='multipart')
    body = resp.json()

    assert resp.status_code == HTTPStatus.CONFLICT

    assert body['errors'] == ['Todas as análises para essa pedido já foram usadas.']


def test_fail_wrong_order_id(client_api_auth, segmentation_order, form_data_segmentation_analysis):

    assert not SegmentationAnalysis.objects.exists()

    url = resolve_url('service:analysis-list-create', segmentation_order.user.uuid, uuid4())

    resp = client_api_auth.post(url, data=form_data_segmentation_analysis, format='multipart')

    assert resp.status_code == HTTPStatus.NOT_FOUND

    assert not SegmentationAnalysis.objects.exists()


def test_fail_with_order_from_another_user(
    client_api_auth,
    user,
    second_user,
    tree_orders_of_two_diff_users,
    form_data_segmentation_analysis,
):
    """
    User must be create analysis only in your own orders
    """

    order_second_user = Order.objects.filter(user=second_user).first()

    url = resolve_url('service:analysis-list-create', user.uuid, order_second_user.uuid)

    resp = client_api_auth.post(url, data=form_data_segmentation_analysis, format='multipart')

    assert resp.status_code == HTTPStatus.NOT_FOUND

    assert not SegmentationAnalysis.objects.exists()


@pytest.mark.parametrize(
    'field, error',
    [
        ('images', ['O campo imagens é obrigatório.']),
        ('analysisName', ['O campo nome da análise é obrigatório.']),
    ],
)
def test_fail_missing_fields(field, error, client_api_auth, segmentation_order, form_data_segmentation_analysis):

    form_data_segmentation_analysis.pop(field)

    url = resolve_url('service:analysis-list-create', segmentation_order.user.uuid, segmentation_order.uuid)

    resp = client_api_auth.post(url, data=form_data_segmentation_analysis, format='multipart')

    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    assert not SegmentationAnalysis.objects.exists()

    assert body['errors'] == error


@pytest.mark.parametrize(
    'field, value, error',
    [
        (
            'analysisName',
            'ss',
            ['Certifique-se de que o nome da análise tenha no mínimo 3 caracteres.'],
        ),
    ],
)
def test_fail_invalid_fields(
    field,
    value,
    error,
    client_api_auth,
    segmentation_order,
    form_data_segmentation_analysis,
):

    form_data_segmentation_analysis[field] = value

    user_uuid = segmentation_order.user.uuid
    order_uuid = segmentation_order.uuid

    url = resolve_url('service:analysis-list-create', user_uuid, order_uuid)
    resp = client_api_auth.post(url, data=form_data_segmentation_analysis, format='multipart')
    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    assert not SegmentationAnalysis.objects.exists()

    assert body['errors'] == error
