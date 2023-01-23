from datetime import datetime
from decimal import Decimal
from http import HTTPStatus
from uuid import uuid4

import pytest
from dj_rest_auth.utils import jwt_encode
from django.core.files.base import ContentFile
from django.shortcuts import resolve_url
from django.utils.timezone import make_aware

from web_server.service.models import ClinicDosimetryAnalysis, Order
from web_server.service.tests.conftest import DATETIME_TIMEZONE


def _verified_unchanged_information_db(clinic_dosimetry):

    analysis_db = ClinicDosimetryAnalysis.objects.get(id=clinic_dosimetry.id)

    assert analysis_db.calibration.uuid == clinic_dosimetry.calibration.uuid
    assert analysis_db.injected_activity == clinic_dosimetry.injected_activity
    assert analysis_db.analysis_name == clinic_dosimetry.analysis_name
    assert analysis_db.administration_datetime == clinic_dosimetry.administration_datetime
    assert analysis_db.images.file.read() == clinic_dosimetry.images.file.read()


# /api/v1/users/<uuid>/order/<uuid>/analysis/<uuid> - PUT


def test_successfull(client_api_auth, second_calibration, clinic_dosi_update_or_del_is_possible):

    update_form_data = {}

    update_form_data['calibrationId'] = second_calibration.uuid
    update_form_data['administrationDatetime'] = make_aware(datetime(2018, 12, 14, 11, 2, 51))
    update_form_data['injectedActivity'] = 100.0
    update_form_data['analysisName'] = 'New analsysis name'
    update_form_data['images'] = ContentFile(b'New File Update', name='images.zip')

    user_uuid = clinic_dosi_update_or_del_is_possible.order.user.uuid
    order_uuid = clinic_dosi_update_or_del_is_possible.order.uuid
    analysis_uuid = clinic_dosi_update_or_del_is_possible.uuid

    url = resolve_url('service:analysis-read-update-delete', user_uuid, order_uuid, analysis_uuid)
    resp = client_api_auth.put(url, data=update_form_data, format='multipart')

    assert resp.status_code == HTTPStatus.NO_CONTENT

    analysis_db = ClinicDosimetryAnalysis.objects.get(id=clinic_dosi_update_or_del_is_possible.id)

    assert analysis_db.calibration.uuid == update_form_data['calibrationId']
    assert analysis_db.injected_activity == update_form_data['injectedActivity']
    assert analysis_db.analysis_name == update_form_data['analysisName']
    assert analysis_db.administration_datetime == update_form_data['administrationDatetime']
    assert analysis_db.images.file.read() == b'New File Update'
    assert analysis_db.status == ClinicDosimetryAnalysis.Status.DATA_SENT


def test_optional_images_successfull(client_api_auth, second_calibration, clinic_dosi_update_or_del_is_possible):

    update_form_data = {}

    update_form_data['calibrationId'] = second_calibration.uuid
    update_form_data['administrationDatetime'] = make_aware(datetime(2018, 12, 14, 11, 2, 51))
    update_form_data['injectedActivity'] = 100.0
    update_form_data['analysisName'] = 'New analsysis name'

    user_uuid = clinic_dosi_update_or_del_is_possible.order.user.uuid
    order_uuid = clinic_dosi_update_or_del_is_possible.order.uuid
    analysis_uuid = clinic_dosi_update_or_del_is_possible.uuid

    url = resolve_url('service:analysis-read-update-delete', user_uuid, order_uuid, analysis_uuid)
    resp = client_api_auth.put(url, data=update_form_data, format='multipart')

    assert resp.status_code == HTTPStatus.NO_CONTENT

    analysis_db = ClinicDosimetryAnalysis.objects.get(id=clinic_dosi_update_or_del_is_possible.id)

    assert analysis_db.calibration.uuid == update_form_data['calibrationId']
    assert analysis_db.injected_activity == update_form_data['injectedActivity']
    assert analysis_db.analysis_name == update_form_data['analysisName']
    assert analysis_db.administration_datetime == update_form_data['administrationDatetime']
    assert analysis_db.images.file.read() == clinic_dosi_update_or_del_is_possible.images.file.read()
    assert analysis_db.status == ClinicDosimetryAnalysis.Status.DATA_SENT


def test_fail_successfull_invalid_status(client_api_auth, second_calibration, clinic_dosimetry):
    """
    The analysis must have INVALID_INFOS or DATA_SENT status
    """

    update_form_data = {}

    update_form_data['calibrationId'] = second_calibration.uuid
    update_form_data['administrationDatetime'] = make_aware(datetime(2018, 12, 14, 11, 2, 51))
    update_form_data['injectedActivity'] = 100.0
    update_form_data['analysisName'] = 'New analsysis name'

    user_uuid = clinic_dosimetry.order.user.uuid
    order_uuid = clinic_dosimetry.order.uuid
    analysis_uuid = clinic_dosimetry.uuid

    url = resolve_url('service:analysis-read-update-delete', user_uuid, order_uuid, analysis_uuid)
    resp = client_api_auth.put(url, data=update_form_data, format='multipart')
    body = resp.json()

    assert resp.status_code == HTTPStatus.CONFLICT

    expected = [
        'Não foi possível excluir/atualizar esta análise.'
        ' Somente análises com o status Informações inválidas ou Dados enviados podem ser excluidas.'
    ]

    assert expected == body['errors']

    _verified_unchanged_information_db(clinic_dosimetry)


def test_fail_wrong_calibration_id(client_api_auth, clinic_dosi_update_or_del_is_possible):

    update_form_data = {}

    update_form_data['calibrationId'] = uuid4()
    update_form_data['administrationDatetime'] = make_aware(datetime(2018, 12, 14, 11, 2, 51))
    update_form_data['injectedActivity'] = 100.0
    update_form_data['analysisName'] = 'New analsysis name'

    user_uuid = clinic_dosi_update_or_del_is_possible.order.user.uuid
    order_uuid = clinic_dosi_update_or_del_is_possible.order.uuid
    analysis_uuid = clinic_dosi_update_or_del_is_possible.uuid

    url = resolve_url('service:analysis-read-update-delete', user_uuid, order_uuid, analysis_uuid)
    resp = client_api_auth.put(url, data=update_form_data, format='multipart')
    body = resp.json()

    assert resp.status_code == HTTPStatus.NOT_FOUND
    assert body['errors'] == ['Calibração com este id não existe para este usuário.']

    _verified_unchanged_information_db(clinic_dosi_update_or_del_is_possible)


def test_fail_wrong_analysis_id(client_api_auth, clinic_dosi_update_or_del_is_possible):

    update_form_data = {}

    update_form_data['calibrationId'] = clinic_dosi_update_or_del_is_possible.calibration.uuid
    update_form_data['administrationDatetime'] = make_aware(datetime(2018, 12, 14, 11, 2, 51))
    update_form_data['injectedActivity'] = 100.0
    update_form_data['analysisName'] = 'New analsysis name'

    user_uuid = clinic_dosi_update_or_del_is_possible.order.user.uuid
    order_uuid = clinic_dosi_update_or_del_is_possible.order.uuid
    analysis_uuid = uuid4()

    url = resolve_url('service:analysis-read-update-delete', user_uuid, order_uuid, analysis_uuid)
    resp = client_api_auth.put(url, data=update_form_data, format='multipart')
    body = resp.json()

    assert resp.status_code == HTTPStatus.NOT_FOUND
    assert body['errors'] == ['Este usuário não possui este recurso cadastrado.']

    _verified_unchanged_information_db(clinic_dosi_update_or_del_is_possible)


def test_fail_wrong_another_order(client_api_auth, user, clinic_dosi_update_or_del_is_possible):

    order = Order.objects.create(
        user=user,
        quantity_of_analyzes=10,
        remaining_of_analyzes=10,
        price=Decimal('1000.00'),
        service_name=Order.ServicesName.CLINIC_DOSIMETRY.value,
    )

    update_form_data = {}

    update_form_data['calibrationId'] = clinic_dosi_update_or_del_is_possible.calibration.uuid
    update_form_data['administrationDatetime'] = make_aware(datetime(2018, 12, 14, 11, 2, 51))
    update_form_data['injectedActivity'] = 100.0
    update_form_data['analysisName'] = 'New analsysis name'

    user_uuid = clinic_dosi_update_or_del_is_possible.order.user.uuid
    order_uuid = order.uuid
    analysis_uuid = clinic_dosi_update_or_del_is_possible.uuid

    url = resolve_url('service:analysis-read-update-delete', user_uuid, order_uuid, analysis_uuid)
    resp = client_api_auth.put(url, data=update_form_data, format='multipart')
    body = resp.json()

    assert resp.status_code == HTTPStatus.NOT_FOUND
    assert body['errors'] == ['Este usuário não possui este recurso cadastrado.']

    _verified_unchanged_information_db(clinic_dosi_update_or_del_is_possible)


def test_fail_wrong_another_user(
    client_api,
    second_user,
    second_user_calibrations,
    clinic_dosi_update_or_del_is_possible,
):

    update_form_data = {}

    update_form_data['calibrationId'] = second_user_calibrations[0].uuid
    update_form_data['administrationDatetime'] = make_aware(datetime(2018, 12, 14, 11, 2, 51))
    update_form_data['injectedActivity'] = 100.0
    update_form_data['analysisName'] = 'New analsysis name'

    user_uuid = second_user.uuid
    order_uuid = clinic_dosi_update_or_del_is_possible.order.uuid
    analysis_uuid = clinic_dosi_update_or_del_is_possible.uuid

    url = resolve_url('service:analysis-read-update-delete', user_uuid, order_uuid, analysis_uuid)

    access_token, _ = jwt_encode(second_user)
    client_api.cookies.load({'jwt-access-token': access_token})

    resp = client_api.put(url, data=update_form_data, format='multipart')
    body = resp.json()

    assert resp.status_code == HTTPStatus.NOT_FOUND
    assert body['errors'] == ['Este usuário não possui este recurso cadastrado.']

    _verified_unchanged_information_db(clinic_dosi_update_or_del_is_possible)


@pytest.mark.parametrize(
    'field, error',
    [
        ('calibrationId', ['calibration_id: Este campo é obrigatório.']),
        ('analysisName', ['analysis_name: Este campo é obrigatório.']),
        ('injectedActivity', ['injected_activity: Este campo é obrigatório.']),
        ('administrationDatetime', ['administration_datetime: Este campo é obrigatório.']),
    ],
)
def test_fail_missing_fields(field, error, client_api_auth, clinic_dosi_update_or_del_is_possible):

    update_form_data = {}

    update_form_data['calibrationId'] = clinic_dosi_update_or_del_is_possible.calibration.uuid
    update_form_data['administrationDatetime'] = make_aware(datetime(2018, 12, 14, 11, 2, 51))
    update_form_data['injectedActivity'] = 100.0
    update_form_data['analysisName'] = 'New analsysis name'

    update_form_data.pop(field)

    user_uuid = clinic_dosi_update_or_del_is_possible.order.user.uuid
    order_uuid = clinic_dosi_update_or_del_is_possible.order.uuid
    analysis_uuid = clinic_dosi_update_or_del_is_possible.uuid

    url = resolve_url('service:analysis-read-update-delete', user_uuid, order_uuid, analysis_uuid)

    resp = client_api_auth.put(url, data=update_form_data, format='multipart')

    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    assert body['errors'] == error

    _verified_unchanged_information_db(clinic_dosi_update_or_del_is_possible)


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
        ('administrationDatetime', 'not is a datatime', ['administration_datetime: Informe uma data/hora válida.']),
    ],
)
def test_fail_invalid_fields(field, value, error, client_api_auth, clinic_dosi_update_or_del_is_possible):

    update_form_data = {}

    update_form_data['calibrationId'] = clinic_dosi_update_or_del_is_possible.calibration.uuid
    update_form_data['administrationDatetime'] = make_aware(datetime(2018, 12, 14, 11, 2, 51))
    update_form_data['injectedActivity'] = 100.0
    update_form_data['analysisName'] = 'New analsysis name'

    update_form_data[field] = value

    user_uuid = clinic_dosi_update_or_del_is_possible.order.user.uuid
    order_uuid = clinic_dosi_update_or_del_is_possible.order.uuid
    analysis_uuid = clinic_dosi_update_or_del_is_possible.uuid

    url = resolve_url('service:analysis-read-update-delete', user_uuid, order_uuid, analysis_uuid)

    resp = client_api_auth.put(url, data=update_form_data, format='multipart')

    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    assert body['errors'] == error

    _verified_unchanged_information_db(clinic_dosi_update_or_del_is_possible)


def test_fail_analysis_name_must_be_unique(
    client_api_auth,
    first_calibration,
    clinic_order,
    clinic_dosi_update_or_del_is_possible,
):

    other_analysis = ClinicDosimetryAnalysis.objects.create(
        calibration=first_calibration,
        order=clinic_order,
        analysis_name='Analysis 2',
        injected_activity=50,
        administration_datetime=DATETIME_TIMEZONE,
        images=ContentFile(b'CT e SPET files 1', name='images.zip'),
    )

    update_form_data = {}

    update_form_data['calibrationId'] = clinic_dosi_update_or_del_is_possible.calibration.uuid
    update_form_data['administrationDatetime'] = make_aware(datetime(2018, 12, 14, 11, 2, 51))
    update_form_data['injectedActivity'] = 100.0
    update_form_data['analysisName'] = other_analysis.analysis_name

    user_uuid = clinic_dosi_update_or_del_is_possible.order.user.uuid
    order_uuid = clinic_dosi_update_or_del_is_possible.order.uuid
    analysis_uuid = clinic_dosi_update_or_del_is_possible.uuid

    url = resolve_url('service:analysis-read-update-delete', user_uuid, order_uuid, analysis_uuid)

    resp = client_api_auth.put(url, data=update_form_data, format='multipart')

    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    assert body['errors'] == ['Dosimetria clínica com este Order e Analysis Name já existe.']

    _verified_unchanged_information_db(clinic_dosi_update_or_del_is_possible)
