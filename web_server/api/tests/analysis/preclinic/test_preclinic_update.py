from decimal import Decimal
from http import HTTPStatus
from uuid import uuid4
from datetime import datetime

import pytest
from django.core.files.base import ContentFile
from django.shortcuts import resolve_url
from django.utils.timezone import make_aware
from web_server.conftest import DATETIME_TIMEZONE


from web_server.service.models import PreClinicDosimetryAnalysis, Order


def _verified_unchanged_information_db(preclinic_dosimetry):

    analysis_db = PreClinicDosimetryAnalysis.objects.get(id=preclinic_dosimetry.id)

    assert analysis_db.calibration.uuid == preclinic_dosimetry.calibration.uuid
    assert analysis_db.injected_activity == preclinic_dosimetry.injected_activity
    assert analysis_db.analysis_name == preclinic_dosimetry.analysis_name
    assert analysis_db.administration_datetime == preclinic_dosimetry.administration_datetime
    assert analysis_db.images.file.read() == preclinic_dosimetry.images.file.read()


def test_update_preclinic_dosimetry_successfull(client_api_auth,
                                                second_calibration,
                                                preclinic_dosimetry_update_delete):
    '''
    /api/v1/users/<uuid>/order/<uuid>/analysis/<uuid> - PUT
    '''
    update_form_data = {}

    update_form_data['calibrationId'] = second_calibration.uuid
    update_form_data['administrationDatetime'] = make_aware(datetime(2018, 12, 14, 11, 2, 51))
    update_form_data['injectedActivity'] = 100.0
    update_form_data['analysisName'] = 'New analsysis name'
    update_form_data['images'] = ContentFile(b'New File Update', name='images.zip')

    user_uuid = preclinic_dosimetry_update_delete.user.uuid
    order_uuid = preclinic_dosimetry_update_delete.order.uuid
    analysis_uuid = preclinic_dosimetry_update_delete.uuid

    url = resolve_url('api:analysis-read-update-delete', user_uuid, order_uuid, analysis_uuid)
    resp = client_api_auth.put(url, data=update_form_data, format='multipart')

    assert resp.status_code == HTTPStatus.NO_CONTENT

    analysis_db = PreClinicDosimetryAnalysis.objects.get(id=preclinic_dosimetry_update_delete.id)

    assert analysis_db.calibration.uuid == update_form_data['calibrationId']
    assert analysis_db.injected_activity == update_form_data['injectedActivity']
    assert analysis_db.analysis_name == update_form_data['analysisName']
    assert analysis_db.administration_datetime == update_form_data['administrationDatetime']
    assert analysis_db.images.file.read() == b'New File Update'
    assert analysis_db.status == PreClinicDosimetryAnalysis.ANALYZING_INFOS


def test_update_preclinic_dosimetry_optional_images_successfull(client_api_auth,
                                                                second_calibration,
                                                                preclinic_dosimetry_update_delete):
    '''
    /api/v1/users/<uuid>/order/<uuid>/analysis/<uuid> - PUT
    '''

    update_form_data = {}

    update_form_data['calibrationId'] = second_calibration.uuid
    update_form_data['administrationDatetime'] = make_aware(datetime(2018, 12, 14, 11, 2, 51))
    update_form_data['injectedActivity'] = 100.0
    update_form_data['analysisName'] = 'New analsysis name'

    user_uuid = preclinic_dosimetry_update_delete.user.uuid
    order_uuid = preclinic_dosimetry_update_delete.order.uuid
    analysis_uuid = preclinic_dosimetry_update_delete.uuid

    url = resolve_url('api:analysis-read-update-delete', user_uuid, order_uuid, analysis_uuid)
    resp = client_api_auth.put(url, data=update_form_data, format='multipart')

    assert resp.status_code == HTTPStatus.NO_CONTENT

    analysis_db = PreClinicDosimetryAnalysis.objects.get(id=preclinic_dosimetry_update_delete.id)

    assert analysis_db.calibration.uuid == update_form_data['calibrationId']
    assert analysis_db.injected_activity == update_form_data['injectedActivity']
    assert analysis_db.analysis_name == update_form_data['analysisName']
    assert analysis_db.administration_datetime == update_form_data['administrationDatetime']
    assert analysis_db.images.file.read() == preclinic_dosimetry_update_delete.images.file.read()
    assert analysis_db.status == PreClinicDosimetryAnalysis.ANALYZING_INFOS


def test_fail_update_preclinic_dosimetry_successfull_invalid_status(client_api_auth,
                                                                    second_calibration,
                                                                    preclinic_dosimetry):
    '''
    /api/v1/users/<uuid>/order/<uuid>/analysis/<uuid> - PUT
    The analysis must have INVALID_INFOS status
    '''

    update_form_data = {}

    update_form_data['calibrationId'] = second_calibration.uuid
    update_form_data['administrationDatetime'] = make_aware(datetime(2018, 12, 14, 11, 2, 51))
    update_form_data['injectedActivity'] = 100.0
    update_form_data['analysisName'] = 'New analsysis name'

    user_uuid = preclinic_dosimetry.user.uuid
    order_uuid = preclinic_dosimetry.order.uuid
    analysis_uuid = preclinic_dosimetry.uuid

    url = resolve_url('api:analysis-read-update-delete', user_uuid, order_uuid, analysis_uuid)
    resp = client_api_auth.put(url, data=update_form_data, format='multipart')
    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    assert body == {'errors': ['Não foi possivel atualizar essa análise.']}

    _verified_unchanged_information_db(preclinic_dosimetry)


def test_fail_update_preclinic_dosimetry_wrong_calibration_id(client_api_auth, preclinic_dosimetry_update_delete):
    '''
    /api/v1/users/<uuid>/order/<uuid>/analysis/<uuid> - PUT
    '''
    update_form_data = {}

    update_form_data['calibrationId'] = uuid4()
    update_form_data['administrationDatetime'] = make_aware(datetime(2018, 12, 14, 11, 2, 51))
    update_form_data['injectedActivity'] = 100.0
    update_form_data['analysisName'] = 'New analsysis name'

    user_uuid = preclinic_dosimetry_update_delete.user.uuid
    order_uuid = preclinic_dosimetry_update_delete.order.uuid
    analysis_uuid = preclinic_dosimetry_update_delete.uuid

    url = resolve_url('api:analysis-read-update-delete', user_uuid, order_uuid, analysis_uuid)
    resp = client_api_auth.put(url, data=update_form_data, format='multipart')
    body = resp.json()

    assert resp.status_code == HTTPStatus.NOT_FOUND
    assert body['errors'] == ['Calibração com esse id não existe para esse usuário.']

    _verified_unchanged_information_db(preclinic_dosimetry_update_delete)


def test_fail_update_preclinic_dosimetry_wrong_analysis_id(client_api_auth, preclinic_dosimetry_update_delete):
    '''
    /api/v1/users/<uuid>/order/<uuid>/analysis/<uuid> - PUT
    '''
    update_form_data = {}

    update_form_data['calibrationId'] = preclinic_dosimetry_update_delete.calibration.uuid
    update_form_data['administrationDatetime'] = make_aware(datetime(2018, 12, 14, 11, 2, 51))
    update_form_data['injectedActivity'] = 100.0
    update_form_data['analysisName'] = 'New analsysis name'

    user_uuid = preclinic_dosimetry_update_delete.user.uuid
    order_uuid = preclinic_dosimetry_update_delete.order.uuid
    analysis_uuid = uuid4()

    url = resolve_url('api:analysis-read-update-delete', user_uuid, order_uuid, analysis_uuid)
    resp = client_api_auth.put(url, data=update_form_data, format='multipart')
    body = resp.json()

    assert resp.status_code == HTTPStatus.NOT_FOUND
    assert body['errors'] == ['Este usuário não possui este recurso cadastrado.']

    _verified_unchanged_information_db(preclinic_dosimetry_update_delete)


def test_fail_update_preclinic_dosimetry_wrong_another_order(client_api_auth, user, preclinic_dosimetry_update_delete):
    '''
    /api/v1/users/<uuid>/order/<uuid>/analysis/<uuid> - PUT
    '''

    order = Order.objects.create(user=user,
                                 quantity_of_analyzes=10,
                                 remaining_of_analyzes=10,
                                 price=Decimal('1000.00'),
                                 service_name=Order.CLINIC_DOSIMETRY
                                 )

    update_form_data = {}

    update_form_data['calibrationId'] = preclinic_dosimetry_update_delete.calibration.uuid
    update_form_data['administrationDatetime'] = make_aware(datetime(2018, 12, 14, 11, 2, 51))
    update_form_data['injectedActivity'] = 100.0
    update_form_data['analysisName'] = 'New analsysis name'

    user_uuid = preclinic_dosimetry_update_delete.user.uuid
    order_uuid = order.uuid
    analysis_uuid = preclinic_dosimetry_update_delete.uuid

    url = resolve_url('api:analysis-read-update-delete', user_uuid, order_uuid, analysis_uuid)
    resp = client_api_auth.put(url, data=update_form_data, format='multipart')
    body = resp.json()

    assert resp.status_code == HTTPStatus.NOT_FOUND
    assert body['errors'] == ['Este usuário não possui este recurso cadastrado.']

    _verified_unchanged_information_db(preclinic_dosimetry_update_delete)


def test_fail_update_preclinic_dosimetry_wrong_another_user(client_api,
                                                            second_user,
                                                            second_user_calibrations,
                                                            preclinic_dosimetry_update_delete):
    '''
    /api/v1/users/<uuid>/order/<uuid>/analysis/<uuid> - PUT
    '''

    update_form_data = {}

    update_form_data['calibrationId'] = second_user_calibrations[0].uuid
    update_form_data['administrationDatetime'] = make_aware(datetime(2018, 12, 14, 11, 2, 51))
    update_form_data['injectedActivity'] = 100.0
    update_form_data['analysisName'] = 'New analsysis name'

    user_uuid = second_user.uuid
    order_uuid = preclinic_dosimetry_update_delete.order.uuid
    analysis_uuid = preclinic_dosimetry_update_delete.uuid

    url = resolve_url('api:analysis-read-update-delete', user_uuid, order_uuid, analysis_uuid)
    client_api.credentials(HTTP_AUTHORIZATION='Bearer ' + second_user.auth_token.key)
    resp = client_api.put(url, data=update_form_data, format='multipart')
    body = resp.json()

    assert resp.status_code == HTTPStatus.NOT_FOUND
    assert body['errors'] == ['Este usuário não possui este recurso cadastrado.']

    _verified_unchanged_information_db(preclinic_dosimetry_update_delete)


@pytest.mark.parametrize('field, error', [
    ('calibrationId', ['O campo id de calibração é obrigatório.']),
    ('analysisName', ['O campo nome da análise é obrigatório.']),
    ('injectedActivity', ['O campo atividade injetada é obrigatório.']),
    ('administrationDatetime', ['O campo hora e data de adminstração é obrigatório.']),
    ])
def test_fail_update_missing_fields(field,
                                    error,
                                    client_api_auth,
                                    preclinic_dosimetry_update_delete):
    '''
    /api/v1/users/<uuid>/order/<uuid>/analysis/<uuid> - PUT
    '''

    update_form_data = {}

    update_form_data['calibrationId'] = preclinic_dosimetry_update_delete.calibration.uuid
    update_form_data['administrationDatetime'] = make_aware(datetime(2018, 12, 14, 11, 2, 51))
    update_form_data['injectedActivity'] = 100.0
    update_form_data['analysisName'] = 'New analsysis name'

    update_form_data.pop(field)

    user_uuid = preclinic_dosimetry_update_delete.user.uuid
    order_uuid = preclinic_dosimetry_update_delete.order.uuid
    analysis_uuid = preclinic_dosimetry_update_delete.uuid

    url = resolve_url('api:analysis-read-update-delete', user_uuid, order_uuid, analysis_uuid)

    resp = client_api_auth.put(url, data=update_form_data, format='multipart')

    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    assert body['errors'] == error

    _verified_unchanged_information_db(preclinic_dosimetry_update_delete)


@pytest.mark.parametrize('field, value, error', [
    ('calibrationId', 'not is uuid', ['Insira um UUID válido.']),
    ('injectedActivity', '-1', ['Certifique-se que atividade injetada seja maior ou igual a 0.0.']),
    ('injectedActivity', 'not ia a number', ['Informe um número.']),
    ('administrationDatetime', 'not is a datatime', ['Informe uma data/hora válida.']),
    ])
def test_fail_update_invalid_fields(field,
                                    value,
                                    error,
                                    client_api_auth,
                                    preclinic_dosimetry_update_delete):
    '''
    /api/v1/users/<uuid>/order/<uuid>/analysis/<uuid> - PUT
    '''

    update_form_data = {}

    update_form_data['calibrationId'] = preclinic_dosimetry_update_delete.calibration.uuid
    update_form_data['administrationDatetime'] = make_aware(datetime(2018, 12, 14, 11, 2, 51))
    update_form_data['injectedActivity'] = 100.0
    update_form_data['analysisName'] = 'New analsysis name'

    update_form_data[field] = value

    user_uuid = preclinic_dosimetry_update_delete.user.uuid
    order_uuid = preclinic_dosimetry_update_delete.order.uuid
    analysis_uuid = preclinic_dosimetry_update_delete.uuid

    url = resolve_url('api:analysis-read-update-delete', user_uuid, order_uuid, analysis_uuid)

    resp = client_api_auth.put(url, data=update_form_data, format='multipart')

    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    assert body['errors'] == error

    _verified_unchanged_information_db(preclinic_dosimetry_update_delete)


def test_fail_update_analysis_name_must_be_unique(client_api_auth,
                                                  user,
                                                  first_calibration,
                                                  preclinic_order,
                                                  preclinic_dosimetry_update_delete):
    '''
    /api/v1/users/<uuid>/order/<uuid>/analysis/<uuid> - PUT
    '''

    other_analysis = PreClinicDosimetryAnalysis.objects.create(
                                                            user=user,
                                                            calibration=first_calibration,
                                                            order=preclinic_order,
                                                            analysis_name='Analysis 2',
                                                            injected_activity=50,
                                                            administration_datetime=DATETIME_TIMEZONE,
                                                            images=ContentFile(b'CT e SPET files 1', name='images.zip')
                                                            )

    update_form_data = {}

    update_form_data['calibrationId'] = preclinic_dosimetry_update_delete.calibration.uuid
    update_form_data['administrationDatetime'] = make_aware(datetime(2018, 12, 14, 11, 2, 51))
    update_form_data['injectedActivity'] = 100.0
    update_form_data['analysisName'] = other_analysis.analysis_name

    user_uuid = preclinic_dosimetry_update_delete.user.uuid
    order_uuid = preclinic_dosimetry_update_delete.order.uuid
    analysis_uuid = preclinic_dosimetry_update_delete.uuid

    url = resolve_url('api:analysis-read-update-delete', user_uuid, order_uuid, analysis_uuid)

    resp = client_api_auth.put(url, data=update_form_data, format='multipart')

    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    assert body['errors'] == ['Análises com esse nome já existe para esse pedido.']

    _verified_unchanged_information_db(preclinic_dosimetry_update_delete)
