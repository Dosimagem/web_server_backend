from http import HTTPStatus
from django.shortcuts import resolve_url
from django.core.exceptions import ValidationError
import pytest

from web_server.service.models import Order, ClinicDosimetryAnalysis, Isotope


@pytest.fixture
def pet_order(user):
    return Order.objects.create(
        user=user,
        quantity_of_analyzes=5,
        remaining_of_analyzes=5,
        price='500.00',
        service_name=Order.ServicesName.CLINIC_DOSIMETRY.value,
        status_payment=Order.PaymentStatus.CONFIRMED,
        equipment_type=Order.EquipmentType.PET,
        equipment_modality=Order.EquipmentModality.PET_CT,
    )


@pytest.fixture
def spect_order(user):
    return Order.objects.create(
        user=user,
        quantity_of_analyzes=5,
        remaining_of_analyzes=5,
        price='500.00',
        service_name=Order.ServicesName.CLINIC_DOSIMETRY.value,
        status_payment=Order.PaymentStatus.CONFIRMED,
        equipment_type=Order.EquipmentType.SPECT,
        equipment_modality=Order.EquipmentModality.SPECT_CT,
    )


def test_order_validation_compatible(user):
    # Valid configurations should not raise validation errors
    order = Order(
        user=user,
        quantity_of_analyzes=5,
        price='500.00',
        service_name=Order.ServicesName.CLINIC_DOSIMETRY.value,
        equipment_type=Order.EquipmentType.SPECT,
        equipment_modality=Order.EquipmentModality.SPECT_CT,
    )
    order.clean()  # Should pass

    order2 = Order(
        user=user,
        quantity_of_analyzes=5,
        price='500.00',
        service_name=Order.ServicesName.CLINIC_DOSIMETRY.value,
        equipment_type=Order.EquipmentType.PET,
        equipment_modality=Order.EquipmentModality.PET_MRI,
    )
    order2.clean()  # Should pass


def test_order_validation_incompatible(user):
    order = Order(
        user=user,
        quantity_of_analyzes=5,
        price='500.00',
        service_name=Order.ServicesName.CLINIC_DOSIMETRY.value,
        equipment_type=Order.EquipmentType.SPECT,
        equipment_modality=Order.EquipmentModality.PET_CT,
    )
    with pytest.raises(ValidationError) as exc:
        order.clean()
    assert 'Modality does not match equipment type SPECT.' in str(exc.value)

    order2 = Order(
        user=user,
        quantity_of_analyzes=5,
        price='500.00',
        service_name=Order.ServicesName.CLINIC_DOSIMETRY.value,
        equipment_type=Order.EquipmentType.PET,
        equipment_modality=Order.EquipmentModality.SPECT_CT,
    )
    with pytest.raises(ValidationError) as exc2:
        order2.clean()
    assert 'Modality does not match equipment type PET.' in str(exc2.value)


def test_pet_flow_successful(client_api_auth, pet_order, clinic_dosimetry_file, lu_177):
    """
    For PET equipment, calibration is optional (bypassed), but isotope must be provided.
    """
    assert not ClinicDosimetryAnalysis.objects.exists()

    payload = {
        'images': clinic_dosimetry_file['images'],
        'analysisName': 'PET Analysis 1',
        'injectedActivity': 150.0,
        'administrationDatetime': '2016-12-14 11:02:51',
        'isotope': lu_177.name,
    }

    url = resolve_url('service:analysis-list-create', pet_order.user.uuid, pet_order.uuid)
    resp = client_api_auth.post(url, data=payload, format='multipart')
    
    assert resp.status_code == HTTPStatus.CREATED
    body = resp.json()

    assert ClinicDosimetryAnalysis.objects.exists()
    analysis = ClinicDosimetryAnalysis.objects.first()

    assert analysis.calibration is None
    assert analysis.isotope == lu_177
    assert body['calibrationId'] is None
    assert body['isotope'] == lu_177.name

    # Verify code generation without calibration
    expected_code = f'{pet_order.user.pk:04}.{pet_order.pk:04}.{lu_177.name}.'
    assert analysis.code.startswith(expected_code)


def test_pet_flow_fail_missing_isotope(client_api_auth, pet_order, clinic_dosimetry_file):
    payload = {
        'images': clinic_dosimetry_file['images'],
        'analysisName': 'PET Analysis 2',
        'injectedActivity': 150.0,
        'administrationDatetime': '2016-12-14 11:02:51',
    }

    url = resolve_url('service:analysis-list-create', pet_order.user.uuid, pet_order.uuid)
    resp = client_api_auth.post(url, data=payload, format='multipart')
    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert 'isotope: Este campo é obrigatório.' in body['errors'][0]


def test_spect_flow_fail_missing_calibration(client_api_auth, spect_order, clinic_dosimetry_file):
    payload = {
        'images': clinic_dosimetry_file['images'],
        'analysisName': 'SPECT Analysis 1',
        'injectedActivity': 150.0,
        'administrationDatetime': '2016-12-14 11:02:51',
    }

    url = resolve_url('service:analysis-list-create', spect_order.user.uuid, spect_order.uuid)
    resp = client_api_auth.post(url, data=payload, format='multipart')
    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert 'calibration_id: Este campo é obrigatório.' in body['errors'][0]


def test_pet_flow_update_successful(client_api_auth, pet_order, clinic_dosimetry_file, lu_177_and_cu_64):
    lu_177 = lu_177_and_cu_64[0]
    cu_64 = lu_177_and_cu_64[1]

    analysis = ClinicDosimetryAnalysis.objects.create(
        order=pet_order,
        analysis_name='PET Analysis Initial',
        injected_activity=100.0,
        administration_datetime='2016-12-14 11:02:51',
        images=clinic_dosimetry_file['images'],
        isotope=lu_177,
        status=ClinicDosimetryAnalysis.Status.INVALID_INFOS,
    )

    update_payload = {
        'analysisName': 'PET Analysis Updated',
        'injectedActivity': 200.0,
        'administrationDatetime': '2016-12-14 11:02:51',
        'isotope': cu_64.name,
    }

    url = resolve_url('service:analysis-read-update-delete', pet_order.user.uuid, pet_order.uuid, analysis.uuid)
    resp = client_api_auth.put(url, data=update_payload, format='multipart')

    assert resp.status_code == HTTPStatus.NO_CONTENT

    analysis.refresh_from_db()
    assert analysis.analysis_name == 'PET Analysis Updated'
    assert analysis.injected_activity == 200.0
    assert analysis.isotope == cu_64
    assert analysis.calibration is None


def test_pet_flow_update_fail_missing_isotope(client_api_auth, pet_order, clinic_dosimetry_file, lu_177):
    analysis = ClinicDosimetryAnalysis.objects.create(
        order=pet_order,
        analysis_name='PET Analysis Initial',
        injected_activity=100.0,
        administration_datetime='2016-12-14 11:02:51',
        images=clinic_dosimetry_file['images'],
        isotope=lu_177,
        status=ClinicDosimetryAnalysis.Status.INVALID_INFOS,
    )

    update_payload = {
        'analysisName': 'PET Analysis Updated',
        'injectedActivity': 200.0,
        'administrationDatetime': '2016-12-14 11:02:51',
    }

    url = resolve_url('service:analysis-read-update-delete', pet_order.user.uuid, pet_order.uuid, analysis.uuid)
    resp = client_api_auth.put(url, data=update_payload, format='multipart')
    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert 'isotope: Este campo é obrigatório.' in body['errors'][0]


def test_spect_flow_update_successful(client_api_auth, spect_order, clinic_dosimetry_file, first_calibration, second_calibration):
    analysis = ClinicDosimetryAnalysis.objects.create(
        order=spect_order,
        analysis_name='SPECT Analysis Initial',
        injected_activity=100.0,
        administration_datetime='2016-12-14 11:02:51',
        images=clinic_dosimetry_file['images'],
        calibration=first_calibration,
        isotope=first_calibration.isotope,
        status=ClinicDosimetryAnalysis.Status.INVALID_INFOS,
    )

    update_payload = {
        'analysisName': 'SPECT Analysis Updated',
        'injectedActivity': 200.0,
        'administrationDatetime': '2016-12-14 11:02:51',
        'calibrationId': second_calibration.uuid,
    }

    url = resolve_url('service:analysis-read-update-delete', spect_order.user.uuid, spect_order.uuid, analysis.uuid)
    resp = client_api_auth.put(url, data=update_payload, format='multipart')

    assert resp.status_code == HTTPStatus.NO_CONTENT

    analysis.refresh_from_db()
    assert analysis.analysis_name == 'SPECT Analysis Updated'
    assert analysis.injected_activity == 200.0
    assert analysis.calibration == second_calibration
    assert analysis.isotope == second_calibration.isotope
