from http import HTTPStatus

from django.shortcuts import resolve_url

from web_server.service.models import Calibration, FORMAT_DATE


def test_list_successful(client_api_auth, first_calibration):
    '''
    /api/v1/users/<uuid>/calibrations/ - GET
    '''

    url = resolve_url('api:calibration-list-create', first_calibration.user.uuid)

    response = client_api_auth.get(url)

    body = response.json()

    assert response.status_code == HTTPStatus.OK

    calibration_db = list(Calibration.objects.filter(user=first_calibration.user))

    calibration_response_list = body['row']

    assert body['count'] == 1

    for cali_response, cali_db in zip(calibration_response_list, calibration_db):
        assert cali_response['id'] == str(cali_db.uuid)
        assert cali_response['userId'] == str(cali_db.user.uuid)
        assert cali_response['isotope'] == cali_db.isotope.name
        assert cali_response['calibrationName'] == cali_db.calibration_name
        assert cali_response['syringeActivity'] == cali_db.syringe_activity
        assert cali_response['residualSyringeActivity'] == cali_db.residual_syringe_activity
        assert cali_response['measurementDatetime'] == cali_db.measurement_datetime.strftime(FORMAT_DATE)
        assert cali_response['phantomVolume'] == cali_db.phantom_volume
        assert cali_response['acquisitionTime'] == cali_db.acquisition_time


def test_try_list_for_user_without_calibrations(client_api_auth, user):
    '''
    /api/v1/users/<uuid>/calibrations/ - GET
    '''

    url = resolve_url('api:calibration-list-create', user.uuid)

    response = client_api_auth.get(url)

    assert response.status_code == HTTPStatus.OK

    body = response.json()

    assert body == {'count': 0, 'row': []}
