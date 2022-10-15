from http import HTTPStatus
from uuid import uuid4

from django.shortcuts import resolve_url

from web_server.core.errors_msg import MSG_ERROR_RESOURCE
from web_server.service.models import Calibration, DosimetryAnalysisBase

# /api/v1/users/<uuid>/calibrations/<uuid> - DELETE


def test_successful(client_api_auth, first_calibration):

    url = resolve_url('service:calibration-read-update-delete', first_calibration.user.uuid, first_calibration.uuid)

    response = client_api_auth.delete(url)

    assert response.status_code == HTTPStatus.OK

    assert not Calibration.objects.exists()

    body = response.json()

    assert 'Calibração deletada com sucesso!' == body['message']


def test_fail_wrong_calibration_id(client_api_auth, first_calibration):

    url = resolve_url('service:calibration-read-update-delete', first_calibration.user.uuid, uuid4())
    response = client_api_auth.delete(url)

    assert response.status_code == HTTPStatus.NOT_FOUND

    body = response.json()

    assert body['errors'] == MSG_ERROR_RESOURCE

    assert Calibration.objects.exists()


def test_fail_delete_calibration_the_another_user(client_api_auth, first_calibration, second_user_calibrations):

    second_user_calibration_uuid = second_user_calibrations[0].uuid

    url = resolve_url(
        'service:calibration-read-update-delete', first_calibration.user.uuid, second_user_calibration_uuid
    )
    response = client_api_auth.delete(url)

    assert response.status_code == HTTPStatus.NOT_FOUND

    body = response.json()

    assert body['errors'] == MSG_ERROR_RESOURCE

    assert Calibration.objects.count() == 3


def test_fail_delete_calibration_used_in_a_clinic_analysis(client_api_auth, clinic_dosimetry):
    """
    Calibrations can be deleted when associated with INVALID_INFOS or DATA_SENT status
    """

    calibration = clinic_dosimetry.calibration

    assert clinic_dosimetry.status == DosimetryAnalysisBase.ANALYZING_INFOS

    url = resolve_url('service:calibration-read-update-delete', calibration.user.uuid, calibration.uuid)

    response = client_api_auth.delete(url)

    assert response.status_code == HTTPStatus.CONFLICT

    assert Calibration.objects.exists()

    body = response.json()

    expected = (
        'Apenas calibrações associadas com análises com o status '
        "Informações Inválidas' ou 'Dados Enviados' podem ser atualizadas/deletadas."
    )

    assert [expected] == body['errors']


def test_fail_delete_calibration_used_in_a_preclinic_analysis(client_api_auth, preclinic_dosimetry):
    """
    Calibrations can be deleted when associated with INVALID_INFOS or DATA_SENT status
    """

    calibration = preclinic_dosimetry.calibration

    assert preclinic_dosimetry.status == DosimetryAnalysisBase.ANALYZING_INFOS

    url = resolve_url('service:calibration-read-update-delete', calibration.user.uuid, calibration.uuid)

    response = client_api_auth.delete(url)

    assert response.status_code == HTTPStatus.CONFLICT

    assert Calibration.objects.exists()

    body = response.json()

    expected = (
        'Apenas calibrações associadas com análises com o status '
        "Informações Inválidas' ou 'Dados Enviados' podem ser atualizadas/deletadas."
    )

    assert [expected] == body['errors']


def test_successful_delete_calibration_used_in_a_analysis(client_api_auth, clinic_dosimetry):
    """
    Calibrations can be deleted when associated with analyzes with Invalid information status
    """

    calibration = clinic_dosimetry.calibration

    clinic_dosimetry.status = DosimetryAnalysisBase.INVALID_INFOS
    clinic_dosimetry.save()

    url = resolve_url('service:calibration-read-update-delete', calibration.user.uuid, calibration.uuid)

    response = client_api_auth.delete(url)

    assert response.status_code == HTTPStatus.OK

    assert not Calibration.objects.exists()

    body = response.json()

    assert 'Calibração deletada com sucesso!' == body['message']
