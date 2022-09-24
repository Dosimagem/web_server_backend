from datetime import datetime

import pytest
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
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
    analyis_1 = ClinicDosimetryAnalysis.objects.create(user=user,
                                                       calibration=first_calibration,
                                                       order=clinic_order,
                                                       analysis_name='Analysis 1',
                                                       injected_activity=50,
                                                       administration_datetime=DATETIME_TIMEZONE,
                                                       images=ContentFile(b'CT e SPET files', name='images.zip')
                                                       )

    analyis_2 = ClinicDosimetryAnalysis.objects.create(user=user,
                                                       calibration=first_calibration,
                                                       order=clinic_order,
                                                       analysis_name='Analysis 2',
                                                       injected_activity=50,
                                                       administration_datetime=DATETIME_TIMEZONE,
                                                       images=ContentFile(b'CT e SPET files', name='images.zip')
                                                       )

    assert user.clinic_dosimetry_analysis.count() == 2

    assert first_calibration.clinic_dosimetry_analysis.count() == 2

    assert clinic_order.clinic_dosimetry_analysis.count() == 2

    assert analyis_1.user == user
    assert analyis_1.calibration == first_calibration
    assert analyis_1.order == clinic_order

    assert analyis_2.user == user
    assert analyis_2.calibration == first_calibration
    assert analyis_2.order == clinic_order


def test_default_values(user, first_calibration, clinic_order):

    analyis = ClinicDosimetryAnalysis.objects.create(user=user,
                                                     calibration=first_calibration,
                                                     order=clinic_order,
                                                     analysis_name='Analysis 1',
                                                     injected_activity=50,
                                                     administration_datetime=DATETIME_TIMEZONE,
                                                     images=ContentFile(b'CT e SPET files', name='images.zip')
                                                     )

    assert analyis.status == ClinicDosimetryAnalysis.ANALYZING_INFOS
    assert analyis.active


def test_str(clinic_dosimetry):

    analyis = ClinicDosimetryAnalysis.objects.first()

    infos = analyis._infos()

    clinic = infos['clinic']
    isotope = infos['isotope']
    year = infos['year']

    assert str(analyis) == f'{clinic:04}.{isotope}.{year}/0001-{ClinicDosimetryAnalysis.CODE}'


def test_status(clinic_dosimetry_info):

    analysis = ClinicDosimetryAnalysis(**clinic_dosimetry_info,
                                       images=ContentFile(b'CT e SPET files', name='images.zip'),
                                       status='AA')

    with pytest.raises(ValidationError):
        analysis.full_clean()


def test_status_options():

    status = ClinicDosimetryAnalysis.STATUS

    assert ClinicDosimetryAnalysis.STATUS == status


def test_model_code_and_service_name():

    assert ClinicDosimetryAnalysis.CODE == 1
    assert ClinicDosimetryAnalysis.SERVICE_NAME_CODE == 'DC'
