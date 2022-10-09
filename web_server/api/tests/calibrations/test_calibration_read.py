from http import HTTPStatus
from uuid import uuid4

from django.shortcuts import resolve_url

from web_server.service.models import FORMAT_DATE
from web_server.core.errors_msg import MSG_ERROR_RESOURCE


def test_read_calibration_successful(client_api_auth, calibration_with_images):
    '''
    /api/v1/users/<uuid>/calibrations/<uuid> - GET
    '''

    url = resolve_url('api:calibration-read-update-delete',
                      calibration_with_images.user.uuid,
                      calibration_with_images.uuid)

    response = client_api_auth.get(url)

    assert response.status_code == HTTPStatus.OK

    body = response.json()

    cali = calibration_with_images

    assert body['id'] == str(cali.uuid)
    assert body['userId'] == str(cali.user.uuid)
    assert body['isotope'] == cali.isotope.name
    assert body['calibrationName'] == cali.calibration_name
    assert body['syringeActivity'] == cali.syringe_activity
    assert body['residualSyringeActivity'] == cali.residual_syringe_activity
    assert body['measurementDatetime'] == cali.measurement_datetime.strftime(FORMAT_DATE)
    assert body['phantomVolume'] == cali.phantom_volume
    assert body['acquisitionTime'] == cali.acquisition_time
    assert body['imagesUrl'].startswith(f'http://testserver/media/{cali.user.id}/calibration')


def test_fail_read_wrong_calibration_id(client_api_auth, first_calibration):
    '''
    /api/v1/users/<uuid>/calibrations/<uuid> - GET
    '''

    url = resolve_url('api:calibration-read-update-delete', first_calibration.user.uuid, uuid4())

    response = client_api_auth.get(url)

    assert response.status_code == HTTPStatus.NOT_FOUND

    body = response.json()

    assert body['errors'] == MSG_ERROR_RESOURCE


def test_fail_read_calibration_the_another_user(client_api_auth, first_calibration, second_user_calibrations):
    '''
    /api/v1/users/<uuid>/calibrations/<uuid> - GET
    '''

    second_user_calibration_uuid = second_user_calibrations[0].uuid

    url = resolve_url('api:calibration-read-update-delete', first_calibration.user.uuid, second_user_calibration_uuid)
    response = client_api_auth.get(url)

    assert response.status_code == HTTPStatus.NOT_FOUND

    body = response.json()

    assert body['errors'] == MSG_ERROR_RESOURCE
