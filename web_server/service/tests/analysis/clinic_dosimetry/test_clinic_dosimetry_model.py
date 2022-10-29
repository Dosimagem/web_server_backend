from datetime import datetime

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile

from web_server.conftest import DATETIME_TIMEZONE
from web_server.service.models import Calibration, ClinicDosimetryAnalysis, Order

User = get_user_model()


def test_create(clinic_dosimetry):
    assert ClinicDosimetryAnalysis.objects.exists()


def test_create_at(clinic_dosimetry):
    assert isinstance(clinic_dosimetry.created_at, datetime)


def test_modified_at(clinic_dosimetry):
    assert isinstance(clinic_dosimetry.modified_at, datetime)


def test_delete_user_must_delete_clinic_dosimetry(user, clinic_dosimetry):
    user.delete()
    assert not ClinicDosimetryAnalysis.objects.exists()


def test_delete_clinic_dosimetry_must_not_delete_user(user, clinic_dosimetry):
    clinic_dosimetry.delete()
    assert User.objects.exists()


def test_delete_calibration_must_delete_clinic_dosimetry(first_calibration, clinic_dosimetry):
    first_calibration.delete()
    assert not ClinicDosimetryAnalysis.objects.exists()


def test_delete_clinic_dosimetry_must_not_delete_calibration(first_calibration, clinic_dosimetry):
    clinic_dosimetry.delete()
    assert Calibration.objects.exists()


def test_delete_order_must_delete_clinic_dosimetry(clinic_order, clinic_dosimetry):
    clinic_order.delete()
    assert not ClinicDosimetryAnalysis.objects.exists()


def test_delete_clinic_dosimetry_must_not_delete_order(clinic_order, clinic_dosimetry):
    clinic_dosimetry.delete()
    assert Order.objects.exists()


def test_clinic_dosimetry_one_to_many_relation(user, first_calibration, clinic_order):
    analyis_1 = ClinicDosimetryAnalysis.objects.create(
        calibration=first_calibration,
        order=clinic_order,
        analysis_name='Analysis 1',
        injected_activity=50,
        administration_datetime=DATETIME_TIMEZONE,
        images=ContentFile(b'CT e SPET files', name='images.zip'),
    )

    analyis_2 = ClinicDosimetryAnalysis.objects.create(
        calibration=first_calibration,
        order=clinic_order,
        analysis_name='Analysis 2',
        injected_activity=50,
        administration_datetime=DATETIME_TIMEZONE,
        images=ContentFile(b'CT e SPET files', name='images.zip'),
    )

    assert first_calibration.clinic_dosimetry_analysis.count() == 2

    assert clinic_order.clinic_dosimetry_analysis.count() == 2

    assert analyis_1.calibration == first_calibration
    assert analyis_1.order == clinic_order

    assert analyis_2.calibration == first_calibration
    assert analyis_2.order == clinic_order


def test_default_values(user, first_calibration, clinic_order):

    analyis = ClinicDosimetryAnalysis.objects.create(
        calibration=first_calibration,
        order=clinic_order,
        analysis_name='Analysis 1',
        injected_activity=50,
        administration_datetime=DATETIME_TIMEZONE,
        images=ContentFile(b'CT e SPET files', name='images.zip'),
    )

    assert analyis.status == ClinicDosimetryAnalysis.Status.DATA_SENT
    assert analyis.active


def test_str(clinic_dosimetry):

    analysis = ClinicDosimetryAnalysis.objects.first()

    clinic_id = analysis.order.user.pk
    isotope = analysis.calibration.isotope
    year = str(analysis.created_at.year)[2:]
    order_id = analysis.order.pk
    analysis_id = analysis.pk
    code = analysis.CODE

    assert str(analysis) == f'{clinic_id:04}.{order_id:04}.{isotope}.{year}/{analysis_id:04}-{code}'


def test_status(clinic_dosimetry_info):

    analysis = ClinicDosimetryAnalysis(
        **clinic_dosimetry_info,
        images=ContentFile(b'CT e SPET files', name='images.zip'),
        status='AA',
    )

    with pytest.raises(ValidationError):
        analysis.full_clean()


def test_model_code_and_service_name():

    assert ClinicDosimetryAnalysis.CODE == '01'
    assert ClinicDosimetryAnalysis.SERVICE_NAME_CODE == 'DC'


def test_save_with_conclude_status_must_be_report(clinic_dosimetry):

    with pytest.raises(ValidationError):
        clinic_dosimetry.status = ClinicDosimetryAnalysis.Status.CONCLUDED
        clinic_dosimetry.full_clean()


def test_order_code(clinic_dosimetry):

    clinic_id = clinic_dosimetry.order.user.id
    year = str(clinic_dosimetry.created_at.year)[2:]
    order_id = clinic_dosimetry.order.id
    analysis_id = clinic_dosimetry.id
    isotope = clinic_dosimetry.calibration.isotope
    expected = f'{clinic_id:04}.{order_id:04}.{isotope}.{year}/{analysis_id:04}-01'

    assert expected == clinic_dosimetry.code
