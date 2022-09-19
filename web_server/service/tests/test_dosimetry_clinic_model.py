from datetime import datetime

import pytest
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

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


def test_delete_calibration_must_delete_clinic_dosimetry(calibration, clinic_dosimetry):
    calibration.delete()
    assert not ClinicDosimetryAnalysis.objects.exists()


def test_delete_clinic_dosimetry_must_not_delete_calibration(calibration, clinic_dosimetry):
    clinic_dosimetry.delete()
    assert Calibration.objects.exists()


def test_delete_order_must_delete_clinic_dosimetry(order, clinic_dosimetry):
    order.delete()
    assert not ClinicDosimetryAnalysis.objects.exists()


def test_delete_clinic_dosimetry_must_not_delete_order(order, clinic_dosimetry):
    clinic_dosimetry.delete()
    assert Order.objects.exists()


def test_clinic_dosimetry_one_to_many_relation(user, calibration, order):

    analyis_1 = ClinicDosimetryAnalysis.objects.create(user=user,
                                                       calibration=calibration,
                                                       order=order,
                                                       images=ContentFile(b'CT e SPET files', name='images.zip')
                                                       )

    analyis_2 = ClinicDosimetryAnalysis.objects.create(user=user,
                                                       calibration=calibration,
                                                       order=order,
                                                       images=ContentFile(b'CT e SPET files', name='images.zip')
                                                       )

    assert user.clinic_dosimetry_analysis.count() == 2

    assert calibration.clinic_dosimetry_analysis.count() == 2

    assert order.clinic_dosimetry_analysis.count() == 2

    assert analyis_1.user == user
    assert analyis_1.calibration == calibration
    assert analyis_1.order == order

    assert analyis_2.user == user
    assert analyis_2.calibration == calibration
    assert analyis_2.order == order


def test_default_values(user, calibration, order):

    analyis = ClinicDosimetryAnalysis.objects.create(user=user,
                                                     calibration=calibration,
                                                     order=order,
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


def test_status(user, calibration, order):

    analysis = ClinicDosimetryAnalysis(user=user,
                                       calibration=calibration,
                                       order=order,
                                       images=ContentFile(b'CT e SPET files', name='images.zip'),
                                       status='AA')

    with pytest.raises(ValidationError):
        analysis.full_clean()
