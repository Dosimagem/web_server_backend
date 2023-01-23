from http import HTTPStatus
from uuid import uuid4

from django.shortcuts import resolve_url

from web_server.core.errors_msg import MSG_ERROR_RESOURCE
from web_server.service.models import Calibration, DosimetryAnalysisBase

# /api/v1/users/<uuid>/calibrations/<uuid> - PUT


def test_successful(client_api_auth, form_data, first_calibration):

    update_form_data = form_data.copy()
    update_form_data['syringeActivity'] = 100.0
    update_form_data['calibrationName'] = 'Calibration new'

    url = resolve_url('service:calibration-read-update-delete', first_calibration.user.uuid, first_calibration.uuid)

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


def test_fail_by_wrong_data(client_api_auth, form_data, first_calibration):

    update_form_data = form_data.copy()
    update_form_data['syringeActivity'] = -100.0

    url = resolve_url('service:calibration-read-update-delete', first_calibration.user.uuid, first_calibration.uuid)

    response = client_api_auth.put(url, data=update_form_data, format='multipart')

    assert response.status_code == HTTPStatus.BAD_REQUEST

    body = response.json()

    expected = ['syringe_activity: Certifique-se que este valor seja maior ou igual a 0.0.']

    assert body['errors'] == expected

    calibration_db = Calibration.objects.first()

    assert calibration_db.uuid == first_calibration.uuid
    assert calibration_db.user.uuid == first_calibration.user.uuid
    assert calibration_db.isotope.name == form_data['isotope']
    assert calibration_db.calibration_name == form_data['calibrationName']
    assert calibration_db.syringe_activity == form_data['syringeActivity']
    assert calibration_db.residual_syringe_activity == form_data['residualSyringeActivity']
    assert calibration_db.measurement_datetime == form_data['measurementDatetime']
    assert calibration_db.phantom_volume == form_data['phantomVolume']
    assert calibration_db.acquisition_time == form_data['acquisitionTime']


def test_fai_isotope_invalid(client_api_auth, first_calibration, form_data):

    url = resolve_url('service:calibration-read-update-delete', first_calibration.user.uuid, first_calibration.uuid)

    update_form_data = form_data.copy()
    update_form_data['isotope'] = 'wrong'

    response = client_api_auth.put(url, data=update_form_data, format='multipart')

    assert response.status_code == HTTPStatus.BAD_REQUEST

    body = response.json()

    expected = ['isotope: Isótopo não registrado.']

    assert body['errors'] == expected

    calibration_db = Calibration.objects.first()

    assert calibration_db.uuid == first_calibration.uuid
    assert calibration_db.user.uuid == first_calibration.user.uuid
    assert calibration_db.isotope.name == form_data['isotope']
    assert calibration_db.calibration_name == form_data['calibrationName']
    assert calibration_db.syringe_activity == form_data['syringeActivity']
    assert calibration_db.residual_syringe_activity == form_data['residualSyringeActivity']
    assert calibration_db.measurement_datetime == form_data['measurementDatetime']
    assert calibration_db.phantom_volume == form_data['phantomVolume']
    assert calibration_db.acquisition_time == form_data['acquisitionTime']


def test_fail_wrong_calibration_id(client_api_auth, form_data, first_calibration):

    url = resolve_url('service:calibration-read-update-delete', first_calibration.user.uuid, uuid4())

    response = client_api_auth.put(url, data=form_data, format='multipart')

    assert response.status_code == HTTPStatus.NOT_FOUND

    body = response.json()

    assert body['errors'] == MSG_ERROR_RESOURCE


def test_fail_update_calibration_the_another_user(
    client_api_auth, form_data, first_calibration, second_user_calibrations
):

    second_user_calibration_uuid = second_user_calibrations[0].uuid

    update_form_data = form_data.copy()
    update_form_data['syringeActivity'] = 100.0
    update_form_data['calibrationName'] = 'Calibration new'

    url = resolve_url(
        'service:calibration-read-update-delete', first_calibration.user.uuid, second_user_calibration_uuid
    )
    response = client_api_auth.put(url, data=form_data, format='multipart')

    assert response.status_code == HTTPStatus.NOT_FOUND

    body = response.json()

    assert body['errors'] == MSG_ERROR_RESOURCE


def test_fail_calibration_name_must_be_unique_per_user(
    client_api_auth, second_calibration, form_data, second_form_data
):

    url = resolve_url('service:calibration-read-update-delete', second_calibration.user.uuid, second_calibration.uuid)

    update_form_data = second_form_data.copy()

    update_form_data['calibrationName'] = form_data['calibrationName']

    response = client_api_auth.put(url, data=update_form_data, format='multipart')

    assert response.status_code == HTTPStatus.BAD_REQUEST

    body = response.json()

    expected = ['Calibração com este User e Calibration Name já existe.']

    assert body['errors'] == expected


def test_fail_calibration_used_in_a_analysis(client_api_auth, clinic_dosimetry, second_form_data):
    """
    Calibrations can be update only when associated with INVALID_INFOS or DATA_SENT status
    """

    calibration = clinic_dosimetry.calibration

    url = resolve_url('service:calibration-read-update-delete', calibration.user.uuid, calibration.uuid)

    update_form_data = second_form_data.copy()

    response = client_api_auth.put(url, data=update_form_data, format='multipart')

    assert response.status_code == HTTPStatus.CONFLICT

    body = response.json()

    expected = (
        'Somente as calibrações associadas a análises com o status '
        "'Informações inválidas' ou 'Dados enviados' podem ser atualizados/excluídos."
    )

    assert [expected] == body['errors']


def test_success_calibration_used_in_a_clinic_analysis(client_api_auth, clinic_dosimetry, form_data, second_form_data):
    """
    Calibrations can be update only when associated with analyzes with Invalid information
    """

    calibration = clinic_dosimetry.calibration
    clinic_dosimetry.status = DosimetryAnalysisBase.Status.INVALID_INFOS
    clinic_dosimetry.save()

    url = resolve_url('service:calibration-read-update-delete', calibration.user.uuid, calibration.uuid)

    update_form_data = second_form_data.copy()

    update_form_data = form_data.copy()
    update_form_data['syringeActivity'] = 100.0
    update_form_data['calibrationName'] = 'Calibration new'

    response = client_api_auth.put(url, data=update_form_data, format='multipart')

    assert response.status_code == HTTPStatus.NO_CONTENT

    calibration_db = Calibration.objects.first()

    assert calibration_db.uuid == calibration.uuid
    assert calibration_db.user.uuid == calibration.user.uuid
    assert calibration_db.isotope.name == update_form_data['isotope']
    assert calibration_db.calibration_name == update_form_data['calibrationName']
    assert calibration_db.syringe_activity == update_form_data['syringeActivity']
    assert calibration_db.residual_syringe_activity == update_form_data['residualSyringeActivity']
    assert calibration_db.measurement_datetime == update_form_data['measurementDatetime']
    assert calibration_db.phantom_volume == update_form_data['phantomVolume']
    assert calibration_db.acquisition_time == update_form_data['acquisitionTime']


def test_success_calibration_used_in_a_preclinic_analysis(
    client_api_auth, preclinic_dosimetry, form_data, second_form_data
):
    """
    Calibrations can be update only when associated with analyzes with Invalid information
    """

    calibration = preclinic_dosimetry.calibration
    preclinic_dosimetry.status = DosimetryAnalysisBase.Status.INVALID_INFOS
    preclinic_dosimetry.save()

    url = resolve_url('service:calibration-read-update-delete', calibration.user.uuid, calibration.uuid)

    update_form_data = second_form_data.copy()

    update_form_data = form_data.copy()
    update_form_data['syringeActivity'] = 100.0
    update_form_data['calibrationName'] = 'Calibration new'

    response = client_api_auth.put(url, data=update_form_data, format='multipart')

    assert response.status_code == HTTPStatus.NO_CONTENT

    calibration_db = Calibration.objects.first()

    assert calibration_db.uuid == calibration.uuid
    assert calibration_db.user.uuid == calibration.user.uuid
    assert calibration_db.isotope.name == update_form_data['isotope']
    assert calibration_db.calibration_name == update_form_data['calibrationName']
    assert calibration_db.syringe_activity == update_form_data['syringeActivity']
    assert calibration_db.residual_syringe_activity == update_form_data['residualSyringeActivity']
    assert calibration_db.measurement_datetime == update_form_data['measurementDatetime']
    assert calibration_db.phantom_volume == update_form_data['phantomVolume']
    assert calibration_db.acquisition_time == update_form_data['acquisitionTime']
