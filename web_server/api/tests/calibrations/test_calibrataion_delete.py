from http import HTTPStatus
from uuid import uuid4

from django.shortcuts import resolve_url

from web_server.service.models import Calibration
from web_server.api.views.errors_msg import MSG_ERROR_RESOURCE


def test_delete_successful(client_api_auth, first_calibration):
    '''
    /api/v1/users/<uuid>/calibrations/<uuid> - DELETE
    '''

    url = resolve_url('api:calibration-read-update-delete', first_calibration.user.uuid, first_calibration.uuid)

    response = client_api_auth.delete(url)

    assert response.status_code == HTTPStatus.OK

    assert not Calibration.objects.exists()

    body = response.json()

    assert body['message'] == 'Calibração deletada com sucesso!'


def test_fail_delete_wrong_calibration_id(client_api_auth, first_calibration):
    '''
    /api/v1/users/<uuid>/calibrations/<uuid> - DELETE
    '''

    url = resolve_url('api:calibration-read-update-delete', first_calibration.user.uuid, uuid4())
    response = client_api_auth.delete(url)

    assert response.status_code == HTTPStatus.NOT_FOUND

    body = response.json()

    assert body['errors'] == MSG_ERROR_RESOURCE

    assert Calibration.objects.exists()


def test_fail_delete_calibration_the_another_user(client_api_auth, first_calibration, second_user_calibrations):
    '''
    /api/v1/users/<uuid>/calibrations/<uuid> - DELETE
    '''

    second_user_calibration_uuid = second_user_calibrations[0].uuid

    url = resolve_url('api:calibration-read-update-delete', first_calibration.user.uuid, second_user_calibration_uuid)
    response = client_api_auth.delete(url)

    assert response.status_code == HTTPStatus.NOT_FOUND

    body = response.json()

    assert body['errors'] == MSG_ERROR_RESOURCE

    assert Calibration.objects.count() == 3
