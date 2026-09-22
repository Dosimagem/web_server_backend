from http import HTTPStatus
from io import BytesIO
from zipfile import ZipFile

import pytest
from django.core.exceptions import ValidationError
from django.shortcuts import resolve_url

from web_server.service.models import Isotope, Order, PreClinicDosimetryAnalysis

@pytest.fixture
def valid_preclinic_zip():
    buffer = BytesIO()

    with ZipFile(buffer, 'w') as zip_file:
        zip_file.writestr('image.dcm', b'DICOM test data')

    buffer.seek(0)
    buffer.name = 'images.zip'
    return buffer
@pytest.fixture
def micro_pet_order(user):
    return Order.objects.create(
        user=user,
        quantity_of_analyzes=5,
        remaining_of_analyzes=5,
        price='500.00',
        service_name=Order.ServicesName.PRECLINIC_DOSIMETRY.value,
        status_payment=Order.PaymentStatus.CONFIRMED,
        equipment_type=Order.EquipmentType.PET,
        equipment_modality=Order.EquipmentModality.MICROPET_CT,
    )


@pytest.fixture
def micro_spect_order(user):
    return Order.objects.create(
        user=user,
        quantity_of_analyzes=5,
        remaining_of_analyzes=5,
        price='500.00',
        service_name=Order.ServicesName.PRECLINIC_DOSIMETRY.value,
        status_payment=Order.PaymentStatus.CONFIRMED,
        equipment_type=Order.EquipmentType.SPECT,
        equipment_modality=Order.EquipmentModality.MICROSPECT_CT,
    )


@pytest.fixture
def f_18(db):
    return Isotope.objects.create(name='F-18', pet=True)


def test_micro_equipment_validation_compatible(user):
    micro_spect = Order(
        user=user,
        quantity_of_analyzes=5,
        price='500.00',
        service_name=Order.ServicesName.PRECLINIC_DOSIMETRY.value,
        equipment_type=Order.EquipmentType.SPECT,
        equipment_modality=Order.EquipmentModality.MICROSPECT_CT,
    )
    micro_spect.clean()

    micro_pet = Order(
        user=user,
        quantity_of_analyzes=5,
        price='500.00',
        service_name=Order.ServicesName.PRECLINIC_DOSIMETRY.value,
        equipment_type=Order.EquipmentType.PET,
        equipment_modality=Order.EquipmentModality.MICROPET_CT,
    )
    micro_pet.clean()


def test_micro_equipment_validation_incompatible(user):
    order = Order(
        user=user,
        quantity_of_analyzes=5,
        price='500.00',
        service_name=Order.ServicesName.PRECLINIC_DOSIMETRY.value,
        equipment_type=Order.EquipmentType.SPECT,
        equipment_modality=Order.EquipmentModality.MICROPET_CT,
    )

    with pytest.raises(ValidationError):
        order.clean()

    order = Order(
        user=user,
        quantity_of_analyzes=5,
        price='500.00',
        service_name=Order.ServicesName.PRECLINIC_DOSIMETRY.value,
        equipment_type=Order.EquipmentType.PET,
        equipment_modality=Order.EquipmentModality.MICROSPECT_CT,
    )

    with pytest.raises(ValidationError):
        order.clean()


def test_micro_pet_flow_successful(
    client_api_auth,
    micro_pet_order,
    valid_preclinic_zip,
    f_18,
):
    payload = {
        'images': valid_preclinic_zip,
        'analysisName': 'microPET Analysis 1',
        'injectedActivity': 20.0,
        'administrationDatetime': '2016-12-14 11:02:51',
        'isotope': f_18.name,
    }

    url = resolve_url(
        'service:analysis-list-create',
        micro_pet_order.user.uuid,
        micro_pet_order.uuid,
    )

    resp = client_api_auth.post(url, data=payload, format='multipart')

    assert resp.status_code == HTTPStatus.CREATED

    analysis = PreClinicDosimetryAnalysis.objects.get()

    assert analysis.calibration is None
    assert analysis.isotope == f_18

    body = resp.json()
    assert body['calibrationId'] is None
    assert body['isotope'] == 'F-18'


def test_micro_pet_flow_fail_missing_isotope(
    client_api_auth,
    micro_pet_order,
    preclinic_dosimetry_file,
):
    payload = {
        'images': preclinic_dosimetry_file['images'],
        'analysisName': 'microPET Analysis 2',
        'injectedActivity': 20.0,
        'administrationDatetime': '2016-12-14 11:02:51',
    }

    url = resolve_url(
        'service:analysis-list-create',
        micro_pet_order.user.uuid,
        micro_pet_order.uuid,
    )

    resp = client_api_auth.post(url, data=payload, format='multipart')

    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert not PreClinicDosimetryAnalysis.objects.exists()


def test_micro_spect_flow_fail_missing_calibration(
    client_api_auth,
    micro_spect_order,
    preclinic_dosimetry_file,
):
    payload = {
        'images': preclinic_dosimetry_file['images'],
        'analysisName': 'microSPECT Analysis 1',
        'injectedActivity': 20.0,
        'administrationDatetime': '2016-12-14 11:02:51',
    }

    url = resolve_url(
        'service:analysis-list-create',
        micro_spect_order.user.uuid,
        micro_spect_order.uuid,
    )

    resp = client_api_auth.post(url, data=payload, format='multipart')

    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert not PreClinicDosimetryAnalysis.objects.exists()
