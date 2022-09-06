from copy import copy
from http import HTTPStatus
from unittest import mock
from uuid import uuid4

import django
from django.shortcuts import resolve_url

from web_server.service.models import Calibration


def test_list_create_not_allowed_method(client_api_auth, calibration):
    '''
    /api/v1/users/<uuid>/calibrations/ - GET, POST
    '''

    url = resolve_url('api:calibration-list-create', calibration.user.uuid)

    resp = client_api_auth.put(url, format='json')
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    resp = client_api_auth.patch(url, format='json')
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    resp = client_api_auth.delete(url, format='json')
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED


def test_list_create_token_view_and_user_id_dont_match(client_api_auth, calibration):
    '''
    /api/v1/users/<uuid>/calibrations/ - GET, POST
    The token does not belong to the user
    '''

    url = resolve_url('api:calibration-list-create', uuid4())
    response = client_api_auth.get(url)

    assert response.status_code == HTTPStatus.UNAUTHORIZED

    body = response.json()

    assert body['errors'] == ['Token and User id do not match.']


def test_list_successful(client_api_auth, calibration):
    '''
    /api/v1/users/<uuid>/calibrations/ - GET
    '''

    url = resolve_url('api:calibration-list-create', calibration.user.uuid)

    response = client_api_auth.get(url)

    body = response.json()

    assert response.status_code == HTTPStatus.OK

    calibration_db = list(Calibration.objects.filter(user=calibration.user))

    calibration_response_list = body['row']

    assert body['count'] == 1

    for cali_response, cali_db in zip(calibration_response_list, calibration_db):
        assert cali_response['id'] == str(cali_db.uuid)
        assert cali_response['userId'] == str(cali_db.user.uuid)
        assert cali_response['isotope'] == cali_db.isotope.name
        assert cali_response['calibrationName'] == cali_db.calibration_name
        assert cali_response['syringeActivity'] == cali_db.syringe_activity
        assert cali_response['residualSyringeActivity'] == cali_db.residual_syringe_activity
        assert cali_response['measurementDatetime'] == cali_db.measurement_datetime.strftime('%d/%m/%Y - %H:%M:%S')
        assert cali_response['phantomVolume'] == cali_db.phantom_volume
        assert cali_response['acquisitionTime'] == str(cali_db.acquisition_time)


def test_try_list_for_user_without_calibrations(client_api_auth, user):
    '''
    /api/v1/users/<uuid>/calibrations/ - GET
    '''

    url = resolve_url('api:calibration-list-create', user.uuid)

    response = client_api_auth.get(url)

    assert response.status_code == HTTPStatus.NOT_FOUND

    body = response.json()

    assert body == {'errors': ['This user has no calibrations record.']}


@mock.patch.object(django.core.files.storage.FileSystemStorage, '_save')
def test_create_successful(save_disk_mock, client_api_auth, user, form_data, calibration_infos):
    '''
    /api/v1/users/<uuid>/calibrations/ - POST
    '''

    save_disk_mock.return_value = 'no save to disk'

    assert not Calibration.objects.exists()

    url = resolve_url('api:calibration-list-create', user.uuid)

    response = client_api_auth.post(url, data=form_data, format='multipart')

    assert response.status_code == HTTPStatus.CREATED

    assert save_disk_mock.call_count == 1

    body = response.json()

    cali_db = Calibration.objects.first()

    assert Calibration.objects.exists()

    assert body['id'] == str(cali_db.uuid)
    assert body['userId'] == str(calibration_infos['user'].uuid)
    assert body['isotope'] == calibration_infos['isotope'].name
    assert body['calibrationName'] == calibration_infos['calibration_name']
    assert body['syringeActivity'] == calibration_infos['syringe_activity']
    assert body['residualSyringeActivity'] == calibration_infos['residual_syringe_activity']
    assert body['measurementDatetime'] == calibration_infos['measurement_datetime'].strftime('%d/%m/%Y - %H:%M:%S')
    assert body['phantomVolume'] == calibration_infos['phantom_volume']
    assert body['acquisitionTime'] == str(calibration_infos['acquisition_time'])


def test_create_fail_negative_float_numbers(client_api_auth, user, form_data):
    '''
    /api/v1/users/<uuid>/calibrations/ - POST
    '''

    url = resolve_url('api:calibration-list-create', user.uuid)

    form_data['syringeActivity'] = -form_data['syringeActivity']
    form_data['residualSyringeActivity'] = -form_data['residualSyringeActivity']
    form_data['phantomVolume'] = -form_data['phantomVolume']

    response = client_api_auth.post(url, data=form_data, format='multipart')

    assert response.status_code == HTTPStatus.BAD_REQUEST

    body = response.json()

    assert not Calibration.objects.exists()

    assert body['errors'] == ['Ensure Syringe_activity value is greater than or equal to 0.0.',
                              'Ensure Residual_syringe_activity value is greater than or equal to 0.0.',
                              'Ensure Phantom_volume value is greater than or equal to 0.0.',
                              ]


@mock.patch.object(django.core.files.storage.FileSystemStorage, '_save')
def test_create_fail_calibration_name_must_be_unique_per_user(save_disk_mock, client_api_auth, user, form_data):
    '''
    /api/v1/users/<uuid>/calibrations/ - POST
    '''

    save_disk_mock.return_value = 'no save to disk'

    url = resolve_url('api:calibration-list-create', user.uuid)

    images = copy(form_data['images'])

    response = client_api_auth.post(url, data=form_data, format='multipart')

    assert response.status_code == HTTPStatus.CREATED

    assert save_disk_mock.call_count == 1

    form_data['images'] = images

    response = client_api_auth.post(url, data=form_data, format='multipart')

    assert response.status_code == HTTPStatus.BAD_REQUEST

    body = response.json()

    assert body['errors'] == ['Calibration with this User and Calibration Name already exists.']


def test_create_fail_datetime_invalid(client_api_auth, user, form_data):
    '''
    /api/v1/users/<uuid>/calibrations/ - POST
    '''

    url = resolve_url('api:calibration-list-create', user.uuid)

    form_data['measurementDatetime'] = 'wrong'
    form_data['acquisitionTime'] = 'wrong'

    response = client_api_auth.post(url, data=form_data, format='multipart')

    assert response.status_code == HTTPStatus.BAD_REQUEST

    body = response.json()

    assert not Calibration.objects.exists()

    assert body['errors'] == ['Enter a valid date/time.', 'Enter a valid time.']


def test_create_fail_isotope_invalid(client_api_auth, user, form_data):
    '''
    /api/v1/users/<uuid>/calibrations/ - POST
    '''

    url = resolve_url('api:calibration-list-create', user.uuid)

    form_data['isotope'] = 'wrong'

    response = client_api_auth.post(url, data=form_data, format='multipart')

    assert response.status_code == HTTPStatus.BAD_REQUEST

    body = response.json()

    assert not Calibration.objects.exists()

    assert body['errors'] == ['Isotope not registered.']


def test_read_update_delete_not_allowed_method(client_api_auth, calibration):
    '''
    /api/v1/users/<uuid>/calibrations/<uuid> - GET, PUT, DELETE
    '''

    url = resolve_url('api:calibration-read-update-delete', calibration.user.uuid, calibration.uuid)

    resp = client_api_auth.patch(url, format='json')
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    resp = client_api_auth.post(url, format='json')
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED


def test_read_update_delete_view_and_user_id_dont_match(client_api_auth, calibration):
    '''
    /api/v1/users/<uuid>/calibrations/<uuid> - GET, PUT, DELETE
    The token does not belong to the user
    '''

    url = resolve_url('api:calibration-read-update-delete', uuid4(), calibration.uuid)
    response = client_api_auth.get(url)

    assert response.status_code == HTTPStatus.UNAUTHORIZED

    body = response.json()

    assert body['errors'] == ['Token and User id do not match.']


def test_delete_successful(client_api_auth, calibration):
    '''
    /api/v1/users/<uuid>/calibrations/<uuid> - DELETE
    '''

    url = resolve_url('api:calibration-read-update-delete', calibration.user.uuid, calibration.uuid)

    response = client_api_auth.delete(url)

    assert response.status_code == HTTPStatus.NO_CONTENT

    assert not Calibration.objects.exists()


def test_delete_fail_wrong_calibration_id(client_api_auth, calibration):
    '''
    /api/v1/users/<uuid>/calibrations/<uuid> - DELETE
    '''

    url = resolve_url('api:calibration-read-update-delete', calibration.user.uuid, uuid4())
    response = client_api_auth.delete(url)

    assert response.status_code == HTTPStatus.NOT_FOUND

    body = response.json()

    assert body['errors'] == ['This user does not have this resource registered.']

    assert Calibration.objects.exists()


@mock.patch.object(django.core.files.storage.FileSystemStorage, '_save')
def test_update_successful(save_disk_mock, client_api_auth, form_data, calibration):
    '''
    /api/v1/users/<uuid>/calibrations/<uuid> - PUT
    '''

    save_disk_mock.return_value = 'no save to disk'

    update_form_data = form_data.copy()
    update_form_data['syringeActivity'] = 100.0
    update_form_data['calibrationName'] = 'Calibration new'

    url = resolve_url('api:calibration-read-update-delete', calibration.user.uuid, calibration.uuid)

    response = client_api_auth.put(url, data=update_form_data, format='multipart')

    assert response.status_code == HTTPStatus.NO_CONTENT

    assert save_disk_mock.call_count == 1

    calibration_db = Calibration.objects.all().first()

    assert calibration_db.uuid == calibration.uuid
    assert calibration_db.user.uuid == calibration.user.uuid
    assert calibration_db.isotope.name == update_form_data['isotope']
    assert calibration_db.calibration_name == update_form_data['calibrationName']
    assert calibration_db.syringe_activity == update_form_data['syringeActivity']
    assert calibration_db.residual_syringe_activity == update_form_data['residualSyringeActivity']
    assert calibration_db.measurement_datetime == update_form_data['measurementDatetime']
    assert calibration_db.phantom_volume == update_form_data['phantomVolume']
    assert calibration_db.acquisition_time == update_form_data['acquisitionTime']


def test_update_fail_by_wrong_data(client_api_auth, form_data, calibration):
    '''
    /api/v1/users/<uuid>/calibrations/<uuid> - PUT
    '''

    update_form_data = form_data.copy()
    update_form_data['syringeActivity'] = -100.0
    update_form_data['acquisitionTime'] = 'wrong'

    url = resolve_url('api:calibration-read-update-delete', calibration.user.uuid, calibration.uuid)

    response = client_api_auth.put(url, data=update_form_data, format='multipart')

    assert response.status_code == HTTPStatus.BAD_REQUEST

    body = response.json()

    assert body['errors'] == ['Enter a valid time.', 'Ensure Syringe_activity value is greater than or equal to 0.0.']

    calibration_db = Calibration.objects.all().first()

    assert calibration_db.uuid == calibration.uuid
    assert calibration_db.user.uuid == calibration.user.uuid
    assert calibration_db.isotope.name == form_data['isotope']
    assert calibration_db.calibration_name == form_data['calibrationName']
    assert calibration_db.syringe_activity == form_data['syringeActivity']
    assert calibration_db.residual_syringe_activity == form_data['residualSyringeActivity']
    assert calibration_db.measurement_datetime == form_data['measurementDatetime']
    assert calibration_db.phantom_volume == form_data['phantomVolume']
    assert calibration_db.acquisition_time == form_data['acquisitionTime']


def test_update_fail_isotope_invalid(client_api_auth, calibration, form_data):
    '''
    /api/v1/users/<uuid>/calibrations/ - POST
    '''

    url = resolve_url('api:calibration-read-update-delete', calibration.user.uuid, calibration.uuid)

    update_form_data = form_data.copy()
    update_form_data['isotope'] = 'wrong'

    response = client_api_auth.put(url, data=update_form_data, format='multipart')

    assert response.status_code == HTTPStatus.BAD_REQUEST

    body = response.json()

    assert body['errors'] == ['Isotope not registered.']

    calibration_db = Calibration.objects.all().first()

    assert calibration_db.uuid == calibration.uuid
    assert calibration_db.user.uuid == calibration.user.uuid
    assert calibration_db.isotope.name == form_data['isotope']
    assert calibration_db.calibration_name == form_data['calibrationName']
    assert calibration_db.syringe_activity == form_data['syringeActivity']
    assert calibration_db.residual_syringe_activity == form_data['residualSyringeActivity']
    assert calibration_db.measurement_datetime == form_data['measurementDatetime']
    assert calibration_db.phantom_volume == form_data['phantomVolume']
    assert calibration_db.acquisition_time == form_data['acquisitionTime']


def test_update_fail_wrong_calibration_id(client_api_auth, form_data, calibration):
    '''
    /api/v1/users/<uuid>/calibrations/<uuid> - PUT
    '''

    url = resolve_url('api:calibration-read-update-delete', calibration.user.uuid, uuid4())

    response = client_api_auth.put(url, data=form_data, format='multipart')

    assert response.status_code == HTTPStatus.NOT_FOUND

    body = response.json()

    assert body['errors'] == ['This user does not have this resource registered.']


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

    assert body['errors'] == ['Calibration with this User and Calibration Name already exists.']
