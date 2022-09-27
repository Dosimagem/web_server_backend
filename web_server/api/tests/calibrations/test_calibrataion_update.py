from http import HTTPStatus
from uuid import uuid4

from django.shortcuts import resolve_url

from web_server.service.models import Calibration
from web_server.api.views.errors_msg import MSG_ERROR_RESOURCE


def test_update_successful(client_api_auth, form_data, first_calibration):
    '''
    /api/v1/users/<uuid>/calibrations/<uuid> - PUT
    '''

    update_form_data = form_data.copy()
    update_form_data['syringeActivity'] = 100.0
    update_form_data['calibrationName'] = 'Calibration new'

    url = resolve_url('api:calibration-read-update-delete', first_calibration.user.uuid, first_calibration.uuid)

    response = client_api_auth.put(url, data=update_form_data, format='multipart')

    assert response.status_code == HTTPStatus.NO_CONTENT

    calibration_db = Calibration.objects.all().first()

    assert calibration_db.uuid == first_calibration.uuid
    assert calibration_db.user.uuid == first_calibration.user.uuid
    assert calibration_db.isotope.name == update_form_data['isotope']
    assert calibration_db.calibration_name == update_form_data['calibrationName']
    assert calibration_db.syringe_activity == update_form_data['syringeActivity']
    assert calibration_db.residual_syringe_activity == update_form_data['residualSyringeActivity']
    assert calibration_db.measurement_datetime == update_form_data['measurementDatetime']
    assert calibration_db.phantom_volume == update_form_data['phantomVolume']
    assert calibration_db.acquisition_time == update_form_data['acquisitionTime']


def test_fail_update_by_wrong_data(client_api_auth, form_data, first_calibration):
    '''
    /api/v1/users/<uuid>/calibrations/<uuid> - PUT
    '''

    update_form_data = form_data.copy()
    update_form_data['syringeActivity'] = -100.0

    url = resolve_url('api:calibration-read-update-delete', first_calibration.user.uuid, first_calibration.uuid)

    response = client_api_auth.put(url, data=update_form_data, format='multipart')

    assert response.status_code == HTTPStatus.BAD_REQUEST

    body = response.json()

    expected = ['Certifique-se que atividade da seringa seja maior ou igual a 0.0.']

    assert body['errors'] == expected

    calibration_db = Calibration.objects.all().first()

    assert calibration_db.uuid == first_calibration.uuid
    assert calibration_db.user.uuid == first_calibration.user.uuid
    assert calibration_db.isotope.name == form_data['isotope']
    assert calibration_db.calibration_name == form_data['calibrationName']
    assert calibration_db.syringe_activity == form_data['syringeActivity']
    assert calibration_db.residual_syringe_activity == form_data['residualSyringeActivity']
    assert calibration_db.measurement_datetime == form_data['measurementDatetime']
    assert calibration_db.phantom_volume == form_data['phantomVolume']
    assert calibration_db.acquisition_time == form_data['acquisitionTime']


def test_fail_update_isotope_invalid(client_api_auth, first_calibration, form_data):
    '''
    /api/v1/users/<uuid>/calibrations/ - POST
    '''

    url = resolve_url('api:calibration-read-update-delete', first_calibration.user.uuid, first_calibration.uuid)

    update_form_data = form_data.copy()
    update_form_data['isotope'] = 'wrong'

    response = client_api_auth.put(url, data=update_form_data, format='multipart')

    assert response.status_code == HTTPStatus.BAD_REQUEST

    body = response.json()

    expected = ['Isotopo não registrado.']

    assert body['errors'] == expected

    calibration_db = Calibration.objects.all().first()

    assert calibration_db.uuid == first_calibration.uuid
    assert calibration_db.user.uuid == first_calibration.user.uuid
    assert calibration_db.isotope.name == form_data['isotope']
    assert calibration_db.calibration_name == form_data['calibrationName']
    assert calibration_db.syringe_activity == form_data['syringeActivity']
    assert calibration_db.residual_syringe_activity == form_data['residualSyringeActivity']
    assert calibration_db.measurement_datetime == form_data['measurementDatetime']
    assert calibration_db.phantom_volume == form_data['phantomVolume']
    assert calibration_db.acquisition_time == form_data['acquisitionTime']


def test_fail_update_wrong_calibration_id(client_api_auth, form_data, first_calibration):
    '''
    /api/v1/users/<uuid>/calibrations/<uuid> - PUT
    '''

    url = resolve_url('api:calibration-read-update-delete', first_calibration.user.uuid, uuid4())

    response = client_api_auth.put(url, data=form_data, format='multipart')

    assert response.status_code == HTTPStatus.NOT_FOUND

    body = response.json()

    assert body['errors'] == MSG_ERROR_RESOURCE


def test_fail_update_calibration_the_another_user(client_api_auth,
                                                  form_data,
                                                  first_calibration,
                                                  second_user_calibrations):
    '''
    /api/v1/users/<uuid>/calibrations/<uuid> - PUT
    '''

    second_user_calibration_uuid = second_user_calibrations[0].uuid

    update_form_data = form_data.copy()
    update_form_data['syringeActivity'] = 100.0
    update_form_data['calibrationName'] = 'Calibration new'

    url = resolve_url('api:calibration-read-update-delete', first_calibration.user.uuid, second_user_calibration_uuid)
    response = client_api_auth.put(url, data=form_data, format='multipart')

    assert response.status_code == HTTPStatus.NOT_FOUND

    body = response.json()

    assert body['errors'] == MSG_ERROR_RESOURCE


def test_update_fail_calibration_name_must_be_unique_per_user(client_api_auth,
                                                              second_calibration,
                                                              form_data,
                                                              second_form_data):
    '''
    /api/v1/users/<uuid>/calibrations/ - POST
    '''

    url = resolve_url('api:calibration-read-update-delete', second_calibration.user.uuid, second_calibration.uuid)

    update_form_data = second_form_data.copy()

    update_form_data['calibrationName'] = form_data['calibrationName']

    response = client_api_auth.put(url, data=update_form_data, format='multipart')

    assert response.status_code == HTTPStatus.BAD_REQUEST

    body = response.json()

    expected = ['Calibração com esse nome ja existe para este usuário.']

    assert body['errors'] == expected
