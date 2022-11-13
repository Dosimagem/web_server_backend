from datetime import datetime

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile

from web_server.service.models import Calibration, Order, PreClinicDosimetryAnalysis
from web_server.service.tests.conftest import DATETIME_TIMEZONE

User = get_user_model()


def test_create(preclinic_dosimetry):
    assert PreClinicDosimetryAnalysis.objects.exists()


def test_create_at(preclinic_dosimetry):
    assert isinstance(preclinic_dosimetry.created_at, datetime)


def test_modified_at(preclinic_dosimetry):
    assert isinstance(preclinic_dosimetry.modified_at, datetime)


def test_delete_user_must_delete_clinic_dosimetry(user, preclinic_dosimetry):
    user.delete()
    assert not PreClinicDosimetryAnalysis.objects.exists()


def test_delete_clinic_dosimetry_must_not_delete_user(user, preclinic_dosimetry):
    preclinic_dosimetry.delete()
    assert User.objects.exists()


def test_delete_calibration_must_delete_clinic_dosimetry(first_calibration, preclinic_dosimetry):
    first_calibration.delete()
    assert not PreClinicDosimetryAnalysis.objects.exists()


def test_delete_clinic_dosimetry_must_not_delete_calibration(first_calibration, preclinic_dosimetry):
    preclinic_dosimetry.delete()
    assert Calibration.objects.exists()


def test_delete_order_must_delete_clinic_dosimetry(preclinic_order, preclinic_dosimetry):
    preclinic_order.delete()
    assert not PreClinicDosimetryAnalysis.objects.exists()


def test_delete_clinic_dosimetry_must_not_delete_order(preclinic_order, preclinic_dosimetry):
    preclinic_dosimetry.delete()
    assert Order.objects.exists()


def test_clinic_dosimetry_one_to_many_relation(user, first_calibration, preclinic_order):

    analysis_1 = PreClinicDosimetryAnalysis.objects.create(
        calibration=first_calibration,
        order=preclinic_order,
        analysis_name='Analysis 1',
        injected_activity=50,
        administration_datetime=DATETIME_TIMEZONE,
        images=ContentFile(b'CT e SPET files', name='images.zip'),
    )

    analysis_2 = PreClinicDosimetryAnalysis.objects.create(
        calibration=first_calibration,
        order=preclinic_order,
        analysis_name='Analysis 2',
        injected_activity=50,
        administration_datetime=DATETIME_TIMEZONE,
        images=ContentFile(b'CT e SPET files', name='images.zip'),
    )

    assert first_calibration.preclinic_dosimetry_analysis.count() == 2

    assert preclinic_order.preclinic_dosimetry_analysis.count() == 2

    assert analysis_1.order.user == user
    assert analysis_1.calibration == first_calibration
    assert analysis_1.order == preclinic_order

    assert analysis_2.order.user == user
    assert analysis_2.calibration == first_calibration
    assert analysis_2.order == preclinic_order


def test_default_values(user, first_calibration, preclinic_order):

    analysis = PreClinicDosimetryAnalysis.objects.create(
        calibration=first_calibration,
        order=preclinic_order,
        analysis_name='Analysis 1',
        injected_activity=50,
        administration_datetime=DATETIME_TIMEZONE,
        images=ContentFile(b'CT e SPET files', name='images.zip'),
    )

    assert analysis.status == PreClinicDosimetryAnalysis.Status.DATA_SENT
    assert analysis.active


def test_str(preclinic_dosimetry):

    analysis = PreClinicDosimetryAnalysis.objects.first()

    clinic_id = analysis.order.user.pk
    isotope = analysis.calibration.isotope
    year = str(analysis.created_at.year)[2:]
    order_id = analysis.order.pk
    analysis_id = analysis.pk
    code = analysis.CODE

    assert str(analysis) == f'{clinic_id:04}.{order_id:04}.{isotope}.{year}/{analysis_id:04}-{code}'


def test_status(preclinic_dosimetry_info):

    analysis = PreClinicDosimetryAnalysis(
        **preclinic_dosimetry_info,
        images=ContentFile(b'CT e SPET files', name='images.zip'),
        status='AA',
    )

    with pytest.raises(ValidationError):
        analysis.full_clean()


def test_model_code_and_service_name():

    assert PreClinicDosimetryAnalysis.CODE == '02'
    assert PreClinicDosimetryAnalysis.SERVICE_NAME_CODE == 'PCD'


def test_save_with_conclude_status_must_be_report(preclinic_dosimetry):

    with pytest.raises(ValidationError):
        preclinic_dosimetry.status = PreClinicDosimetryAnalysis.Status.CONCLUDED
        preclinic_dosimetry.full_clean()


def test_order_code(preclinic_dosimetry):

    clinic_id = preclinic_dosimetry.order.user.id
    year = str(preclinic_dosimetry.created_at.year)[2:]
    order_id = preclinic_dosimetry.order.id
    analysis_id = preclinic_dosimetry.id
    isotope = preclinic_dosimetry.calibration.isotope
    expected = f'{clinic_id:04}.{order_id:04}.{isotope}.{year}/{analysis_id:04}-02'

    assert expected == preclinic_dosimetry.code


def test_get_absolute_url(preclinic_dosimetry):

    user_id = preclinic_dosimetry.order.user.uuid
    order_id = preclinic_dosimetry.order.uuid

    expected = f'/api/v1/users/{user_id}/orders/{order_id}/analysis/{preclinic_dosimetry.uuid}'

    assert expected == preclinic_dosimetry.get_absolute_url()
