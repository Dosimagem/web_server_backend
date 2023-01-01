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


def test_successfull(client_api_auth, preclinic_order, form_data_preclinic_dosimetry):
    """
    After analyses create order remaining of analyzes must be decreased by one
    """

    assert not ClinicDosimetryAnalysis.objects.exists()
    assert not PreClinicDosimetryAnalysis.objects.exists()
    assert not SegmentationAnalysis.objects.exists()
    assert not RadiosynoAnalysis.objects.exists()

    assert Order.objects.get(id=preclinic_order.id).remaining_of_analyzes == preclinic_order.remaining_of_analyzes

    url = resolve_url(
        'service:analysis-list-create',
        preclinic_order.user.uuid,
        preclinic_order.uuid,
    )
    resp = client_api_auth.post(url, data=form_data_preclinic_dosimetry, format='multipart')
    body = resp.json()

    assert resp.status_code == HTTPStatus.CREATED

    assert not ClinicDosimetryAnalysis.objects.exists()
    assert PreClinicDosimetryAnalysis.objects.exists()
    assert not SegmentationAnalysis.objects.exists()
    assert not RadiosynoAnalysis.objects.exists()

    preclinic_db = PreClinicDosimetryAnalysis.objects.first()

    user_id = preclinic_db.order.user.uuid
    order_id = preclinic_db.order.uuid

    expected = f'/api/v1/users/{user_id}/orders/{order_id}/analysis/{preclinic_db.uuid}'

    assert expected == resp.headers['Location']

    assert Order.objects.get(id=preclinic_order.id).remaining_of_analyzes == preclinic_order.remaining_of_analyzes - 1

    assert body['id'] == str(preclinic_db.uuid)
    assert body['userId'] == str(preclinic_db.order.user.uuid)
    assert body['orderId'] == str(preclinic_db.order.uuid)
    assert body['calibrationId'] == str(preclinic_db.calibration.uuid)
    assert body['status'] == preclinic_db.get_status_display()
    assert body['active'] == preclinic_db.active
    assert body['serviceName'] == preclinic_db.order.get_service_name_display()
    assert body['createdAt'] == preclinic_db.created_at.strftime(FORMAT_DATE)
    assert body['modifiedAt'] == preclinic_db.modified_at.strftime(FORMAT_DATE)

    assert body['injectedActivity'] == preclinic_db.injected_activity
    assert body['analysisName'] == preclinic_db.analysis_name
    assert body['administrationDatetime'] == preclinic_db.administration_datetime.strftime(FORMAT_DATE)

    # TODO: gerar a url completa
    assert body['imagesUrl'].startswith(f'http://testserver/media/{preclinic_db.order.user.id}')

    assert body['report'] == ''


def test_fail_order_must_have_payment_confirmed(client_api_auth, preclinic_order, form_data_preclinic_dosimetry):

    preclinic_order.status_payment = Order.PaymentStatus.AWAITING_PAYMENT
    preclinic_order.save()

    assert not PreClinicDosimetryAnalysis.objects.exists()

    url = resolve_url('service:analysis-list-create', preclinic_order.user.uuid, preclinic_order.uuid)

    resp = client_api_auth.post(url, data=form_data_preclinic_dosimetry, format='multipart')
    body = resp.json()

    assert resp.status_code == HTTPStatus.CONFLICT

    assert not PreClinicDosimetryAnalysis.objects.exists()

    assert ['O pagamento desse pedido não foi confirmado.'] == body['errors']


def test_fail_wrong_administration_datetime(client_api_auth, preclinic_order, form_data_preclinic_dosimetry):

    form_data_preclinic_dosimetry['administration_datetime'] = 'w'

    assert not PreClinicDosimetryAnalysis.objects.exists()

    url = resolve_url(
        'service:analysis-list-create',
        preclinic_order.user.uuid,
        preclinic_order.uuid,
    )

    resp = client_api_auth.post(url, data=form_data_preclinic_dosimetry, format='multipart')
    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    assert not PreClinicDosimetryAnalysis.objects.exists()

    assert body['errors'] == ['Informe uma data/hora válida.']


def test_fail_injected_activity_must_be_positive(client_api_auth, preclinic_order, form_data_preclinic_dosimetry):

    form_data_preclinic_dosimetry['injectedActivity'] = -form_data_preclinic_dosimetry['injectedActivity']

    assert not PreClinicDosimetryAnalysis.objects.exists()

    url = resolve_url(
        'service:analysis-list-create',
        preclinic_order.user.uuid,
        preclinic_order.uuid,
    )

    resp = client_api_auth.post(url, data=form_data_preclinic_dosimetry, format='multipart')
    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    assert not PreClinicDosimetryAnalysis.objects.exists()

    assert body['errors'] == ['Certifique-se que atividade injetada seja maior ou igual a 0.0.']


def test_fail_analisys_name_must_be_unique_per_order(
    client_api_auth,
    user,
    form_data_preclinic_dosimetry,
    preclinic_dosimetry_info,
    preclinic_dosimetry_file,
):
    """
    The analysis name must be unique in an order
    """

    order = preclinic_dosimetry_info['order']

    images = deepcopy(preclinic_dosimetry_file['images'])

    PreClinicDosimetryAnalysis.objects.create(**preclinic_dosimetry_info, **preclinic_dosimetry_file)

    assert PreClinicDosimetryAnalysis.objects.count() == 1

    form_data_preclinic_dosimetry['images'] = images

    url = resolve_url('service:analysis-list-create', user.uuid, order.uuid)
    resp = client_api_auth.post(url, data=form_data_preclinic_dosimetry, format='multipart')
    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    assert PreClinicDosimetryAnalysis.objects.count() == 1

    assert body['errors'] == ['Análises com esse nome já existe para esse pedido.']


def test_fail_not_have_remaining_of_analyzes(client_api_auth, user, form_data_preclinic_dosimetry):
    """
    All requests for quotas have already been used in use
    """

    order = Order.objects.create(
        user=user,
        quantity_of_analyzes=3,
        remaining_of_analyzes=0,
        price=Decimal('3000.00'),
        service_name=Order.ServicesName.PRECLINIC_DOSIMETRY.value,
        status_payment=Order.PaymentStatus.AWAITING_PAYMENT,
        active=True,
    )

    url = resolve_url('service:analysis-list-create', user.uuid, order.uuid)
    resp = client_api_auth.post(url, data=form_data_preclinic_dosimetry, format='multipart')
    body = resp.json()

    assert resp.status_code == HTTPStatus.CONFLICT

    assert not PreClinicDosimetryAnalysis.objects.exists()

    assert body['errors'] == ['Todas as análises para essa pedido já foram usadas.']


def test_fail_wrong_calibration_id(client_api_auth, preclinic_order, form_data_preclinic_dosimetry):

    form_data_preclinic_dosimetry['calibrationId'] = uuid4()

    assert not PreClinicDosimetryAnalysis.objects.exists()

    url = resolve_url(
        'service:analysis-list-create',
        preclinic_order.user.uuid,
        preclinic_order.uuid,
    )

    resp = client_api_auth.post(url, data=form_data_preclinic_dosimetry, format='multipart')

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    assert not PreClinicDosimetryAnalysis.objects.exists()

    body = resp.json()

    assert body['errors'] == ['Calibração com esse id não existe para esse usuário.']


def test_fail_wrong__order_id(client_api_auth, preclinic_order, form_data_preclinic_dosimetry):

    assert not PreClinicDosimetryAnalysis.objects.exists()

    url = resolve_url('service:analysis-list-create', preclinic_order.user.uuid, uuid4())

    resp = client_api_auth.post(url, data=form_data_preclinic_dosimetry, format='multipart')

    assert resp.status_code == HTTPStatus.NOT_FOUND

    assert not PreClinicDosimetryAnalysis.objects.exists()


def test_fail_with_order_from_another_user(
    client_api,
    user,
    second_user,
    tree_orders_of_two_diff_users,
    form_data_preclinic_dosimetry,
):
    """
    User must be create analysis only in your own orders
    """

    order_first_user = Order.objects.filter(user=user).first()

    url = resolve_url('service:analysis-list-create', second_user.uuid, order_first_user.uuid)

    access_token, _ = jwt_encode(second_user)
    client_api.cookies.load({'jwt-access-token': access_token})

    resp = client_api.post(url, data=form_data_preclinic_dosimetry, format='multipart')

    assert resp.status_code == HTTPStatus.NOT_FOUND

    assert not PreClinicDosimetryAnalysis.objects.exists()


@pytest.mark.parametrize(
    'field, error',
    [
        ('calibrationId', ['O campo id de calibração é obrigatório.']),
        ('images', ['O campo imagens é obrigatório.']),
        ('analysisName', ['O campo nome da análise é obrigatório.']),
        ('injectedActivity', ['O campo atividade injetada é obrigatório.']),
        (
            'administrationDatetime',
            ['O campo hora e data de adminstração é obrigatório.'],
        ),
    ],
)
def test_fail_missing_fields(
    field,
    error,
    client_api_auth,
    preclinic_order,
    form_data_preclinic_dosimetry,
):

    form_data_preclinic_dosimetry.pop(field)

    url = resolve_url(
        'service:analysis-list-create',
        preclinic_order.user.uuid,
        preclinic_order.uuid,
    )

    resp = client_api_auth.post(url, data=form_data_preclinic_dosimetry, format='multipart')

    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    assert not PreClinicDosimetryAnalysis.objects.exists()

    assert body['errors'] == error


def test_fail_with_calibration_of_another_user(
    client_api_auth,
    preclinic_order,
    second_user_calibrations,
    form_data_preclinic_dosimetry,
):

    assert not PreClinicDosimetryAnalysis.objects.exists()

    form_data_preclinic_dosimetry['calibrationId'] = second_user_calibrations[0].uuid

    url = resolve_url(
        'service:analysis-list-create',
        preclinic_order.user.uuid,
        preclinic_order.uuid,
    )
    resp = client_api_auth.post(url, data=form_data_preclinic_dosimetry, format='multipart')
    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    assert not PreClinicDosimetryAnalysis.objects.exists()

    assert body['errors'] == ['Calibração com esse id não existe para esse usuário.']


@pytest.mark.parametrize(
    'field, value, error',
    [
        ('calibrationId', 'not is uuid', ['Insira um UUID válido.']),
        (
            'injectedActivity',
            '-1',
            ['Certifique-se que atividade injetada seja maior ou igual a 0.0.'],
        ),
        ('injectedActivity', 'not ia a number', ['Informe um número.']),
        (
            'administrationDatetime',
            'not is a datatime',
            ['Informe uma data/hora válida.'],
        ),
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
    preclinic_order,
    form_data_preclinic_dosimetry,
):

    form_data_preclinic_dosimetry[field] = value

    url = resolve_url(
        'service:analysis-list-create',
        preclinic_order.user.uuid,
        preclinic_order.uuid,
    )
    resp = client_api_auth.post(url, data=form_data_preclinic_dosimetry, format='multipart')
    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    assert not PreClinicDosimetryAnalysis.objects.exists()

    assert body['errors'] == error
