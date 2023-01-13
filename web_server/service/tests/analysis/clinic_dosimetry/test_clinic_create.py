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
    RadiosynoAnalysis,
    SegmentationAnalysis,
)

# /api/v1/users/<uuid>/order/<uuid>/analysis/ - POST


def test_successful(client_api_auth, clinic_order, form_data_clinic_dosimetry):
    """
    After analyses create order remaining of analyzes must be decreased by one
    """

    assert not ClinicDosimetryAnalysis.objects.exists()
    assert not PreClinicDosimetryAnalysis.objects.exists()
    assert not SegmentationAnalysis.objects.exists()
    assert not RadiosynoAnalysis.objects.exists()

    assert Order.objects.get(id=clinic_order.id).remaining_of_analyzes == clinic_order.remaining_of_analyzes

    url = resolve_url('service:analysis-list-create', clinic_order.user.uuid, clinic_order.uuid)
    resp = client_api_auth.post(url, data=form_data_clinic_dosimetry, format='multipart')
    body = resp.json()

    assert HTTPStatus.CREATED == resp.status_code

    assert ClinicDosimetryAnalysis.objects.exists()
    assert not PreClinicDosimetryAnalysis.objects.exists()
    assert not SegmentationAnalysis.objects.exists()
    assert not RadiosynoAnalysis.objects.exists()

    clinic_dosi_db = ClinicDosimetryAnalysis.objects.first()

    expected = f'/api/v1/users/{clinic_order.user.uuid}/orders/{clinic_order.uuid}/analysis/{clinic_dosi_db.uuid}'

    assert expected == resp.headers['Location']

    assert Order.objects.get(id=clinic_order.id).remaining_of_analyzes == clinic_order.remaining_of_analyzes - 1

    assert body['id'] == str(clinic_dosi_db.uuid)
    assert body['userId'] == str(clinic_dosi_db.order.user.uuid)
    assert body['orderId'] == str(clinic_dosi_db.order.uuid)
    assert body['calibrationId'] == str(clinic_dosi_db.calibration.uuid)
    assert body['status'] == clinic_dosi_db.get_status_display()
    assert body['active'] == clinic_dosi_db.active
    assert body['serviceName'] == clinic_dosi_db.order.get_service_name_display()
    assert body['createdAt'] == clinic_dosi_db.created_at.strftime(FORMAT_DATE)
    assert body['modifiedAt'] == clinic_dosi_db.modified_at.strftime(FORMAT_DATE)

    assert body['injectedActivity'] == clinic_dosi_db.injected_activity
    assert body['analysisName'] == clinic_dosi_db.analysis_name
    assert body['administrationDatetime'] == clinic_dosi_db.administration_datetime.strftime(FORMAT_DATE)

    # TODO: Pensar uma forma melhor
    assert body['imagesUrl'].startswith(f'http://testserver/media/{clinic_dosi_db.order.user.id}')


def test_fail_order_must_have_payment_confirmed(client_api_auth, clinic_order, form_data_clinic_dosimetry):

    clinic_order.status_payment = Order.PaymentStatus.AWAITING_PAYMENT
    clinic_order.save()

    assert not ClinicDosimetryAnalysis.objects.exists()

    url = resolve_url('service:analysis-list-create', clinic_order.user.uuid, clinic_order.uuid)

    resp = client_api_auth.post(url, data=form_data_clinic_dosimetry, format='multipart')
    body = resp.json()

    assert resp.status_code == HTTPStatus.PAYMENT_REQUIRED

    assert not ClinicDosimetryAnalysis.objects.exists()

    assert ['O pagamento deste pedido não foi confirmado.'] == body['errors']


def test_fail_wrong_administration_datetime(client_api_auth, clinic_order, form_data_clinic_dosimetry):

    form_data_clinic_dosimetry['administrationDatetime'] = 'w'

    assert not ClinicDosimetryAnalysis.objects.exists()

    url = resolve_url('service:analysis-list-create', clinic_order.user.uuid, clinic_order.uuid)

    resp = client_api_auth.post(url, data=form_data_clinic_dosimetry, format='multipart')
    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    assert not ClinicDosimetryAnalysis.objects.exists()

    assert body['errors'] == ['administration_datetime: Informe uma data/hora válida.']


def test_fail_activity_must_be_positive(client_api_auth, clinic_order, form_data_clinic_dosimetry):

    form_data_clinic_dosimetry['injectedActivity'] = -form_data_clinic_dosimetry['injectedActivity']

    assert not ClinicDosimetryAnalysis.objects.exists()

    url = resolve_url(
        'service:analysis-list-create',
        clinic_order.user.uuid,
        clinic_order.uuid,
    )

    resp = client_api_auth.post(url, data=form_data_clinic_dosimetry, format='multipart')
    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    assert not ClinicDosimetryAnalysis.objects.exists()

    assert body['errors'] == ['injected_activity: Certifique-se que este valor seja maior ou igual a 0.0.']


def test_fail_analisys_name_must_be_unique_per_order(
    client_api_auth,
    form_data_clinic_dosimetry,
    clinic_dosimetry_info,
    clinic_dosimetry_file,
):
    """
    The analysis name must be unique in an order
    """

    order = clinic_dosimetry_info['order']

    images = deepcopy(clinic_dosimetry_file['images'])

    ClinicDosimetryAnalysis.objects.create(**clinic_dosimetry_info, **clinic_dosimetry_file)

    assert ClinicDosimetryAnalysis.objects.count() == 1

    form_data_clinic_dosimetry['images'] = images

    url = resolve_url('service:analysis-list-create', order.user.uuid, order.uuid)
    resp = client_api_auth.post(url, data=form_data_clinic_dosimetry, format='multipart')
    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    assert ClinicDosimetryAnalysis.objects.count() == 1

    assert body['errors'] == ['Clinic Dosimetry com este Order e Analysis Name já existe.']


def test_fail_not_have_remaining_of_analyzes(client_api_auth, user, form_data_clinic_dosimetry):
    """
    All requests for quotas have already been used in use
    """

    order = Order.objects.create(
        user=user,
        quantity_of_analyzes=3,
        price=Decimal('3000.00'),
        service_name=Order.ServicesName.CLINIC_DOSIMETRY.value,
        status_payment=Order.PaymentStatus.AWAITING_PAYMENT,
        active=True,
    )

    order.remaining_of_analyzes = 0
    order.save()

    url = resolve_url('service:analysis-list-create', user.uuid, order.uuid)
    resp = client_api_auth.post(url, data=form_data_clinic_dosimetry, format='multipart')
    body = resp.json()

    assert resp.status_code == HTTPStatus.CONFLICT

    assert not ClinicDosimetryAnalysis.objects.exists()

    assert body['errors'] == ['Todas as análises deste pedido já foram usadas.']


def test_fail_missing_calibration_id(client_api_auth, clinic_order, form_data_clinic_dosimetry):

    form_data_clinic_dosimetry.pop('calibrationId')

    assert not ClinicDosimetryAnalysis.objects.exists()

    url = resolve_url('service:analysis-list-create', clinic_order.user.uuid, clinic_order.uuid)

    resp = client_api_auth.post(url, data=form_data_clinic_dosimetry, format='multipart')

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    assert not ClinicDosimetryAnalysis.objects.exists()

    body = resp.json()

    assert body['errors'] == ['calibration_id: Este campo é obrigatório.']


def test_fail_wrong_calibration_id(client_api_auth, clinic_order, form_data_clinic_dosimetry):

    form_data_clinic_dosimetry['calibrationId'] = uuid4()

    assert not ClinicDosimetryAnalysis.objects.exists()

    url = resolve_url('service:analysis-list-create', clinic_order.user.uuid, clinic_order.uuid)

    resp = client_api_auth.post(url, data=form_data_clinic_dosimetry, format='multipart')

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    assert not ClinicDosimetryAnalysis.objects.exists()

    body = resp.json()

    assert body['errors'] == ['Calibração com este id não existe para este usuário.']


def test_fail_wrong_order_id(client_api_auth, clinic_order, form_data_clinic_dosimetry):

    assert not ClinicDosimetryAnalysis.objects.exists()

    url = resolve_url('service:analysis-list-create', clinic_order.user.uuid, uuid4())

    resp = client_api_auth.post(url, data=form_data_clinic_dosimetry, format='multipart')

    assert resp.status_code == HTTPStatus.NOT_FOUND

    assert not ClinicDosimetryAnalysis.objects.exists()


def test_fail_with_order_from_another_user(
    client_api_auth,
    user,
    second_user,
    tree_orders_of_two_diff_users,
    form_data_clinic_dosimetry,
):
    """
    User must be create analysis only in your own orders
    """

    order_second_user = Order.objects.filter(user=second_user).first()

    url = resolve_url('service:analysis-list-create', user.uuid, order_second_user.uuid)

    resp = client_api_auth.post(url, data=form_data_clinic_dosimetry, format='multipart')

    assert resp.status_code == HTTPStatus.NOT_FOUND

    assert not ClinicDosimetryAnalysis.objects.exists()


def test_fail_whith_calibration_of_another_user(
    client_api_auth,
    clinic_order,
    second_user_calibrations,
    form_data_clinic_dosimetry,
):

    assert not ClinicDosimetryAnalysis.objects.exists()

    form_data_clinic_dosimetry['calibrationId'] = second_user_calibrations[0].uuid

    url = resolve_url('service:analysis-list-create', clinic_order.user.uuid, clinic_order.uuid)
    resp = client_api_auth.post(url, data=form_data_clinic_dosimetry, format='multipart')
    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    assert not ClinicDosimetryAnalysis.objects.exists()

    assert body['errors'] == ['Calibração com este id não existe para este usuário.']


@pytest.mark.parametrize(
    'field, error',
    [
        ('calibrationId', ['calibration_id: Este campo é obrigatório.']),
        ('images', ['images: Este campo é obrigatório.']),
        ('analysisName', ['analysis_name: Este campo é obrigatório.']),
        ('injectedActivity', ['injected_activity: Este campo é obrigatório.']),
        ('administrationDatetime', ['administration_datetime: Este campo é obrigatório.']),
    ],
)
def test_fail_missing_fields(field, error, client_api_auth, clinic_order, form_data_clinic_dosimetry):

    form_data_clinic_dosimetry.pop(field)

    url = resolve_url('service:analysis-list-create', clinic_order.user.uuid, clinic_order.uuid)

    resp = client_api_auth.post(url, data=form_data_clinic_dosimetry, format='multipart')

    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    assert not ClinicDosimetryAnalysis.objects.exists()

    assert body['errors'] == error


@pytest.mark.parametrize(
    'field, value, error',
    [
        ('calibrationId', 'not is uuid', ['calibration_id: Insira um UUID válido.']),
        (
            'injectedActivity',
            '-1',
            ['injected_activity: Certifique-se que este valor seja maior ou igual a 0.0.'],
        ),
        ('injectedActivity', 'not ia a number', ['injected_activity: Informe um número.']),
        (
            'administrationDatetime',
            'not is a datatime',
            ['administration_datetime: Informe uma data/hora válida.'],
        ),
        (
            'analysisName',
            'ss',
            ['analysis_name: Certifique-se de que o valor tenha no mínimo 3 caracteres (ele possui 2).'],
        ),
    ],
)
def test_fail_invalid_fields(
    field,
    value,
    error,
    client_api_auth,
    clinic_order,
    form_data_clinic_dosimetry,
):

    form_data_clinic_dosimetry[field] = value

    user_uuid = clinic_order.user.uuid
    order_uuid = clinic_order.uuid

    url = resolve_url('service:analysis-list-create', user_uuid, order_uuid)
    resp = client_api_auth.post(url, data=form_data_clinic_dosimetry, format='multipart')
    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    assert not ClinicDosimetryAnalysis.objects.exists()

    assert body['errors'] == error
