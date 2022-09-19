from datetime import datetime

import pytest
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from web_server.service.models import Calibration, PreClinicDosimetryAnalysis, Order


User = get_user_model()


@pytest.fixture
def preclinic_dosimetry_analysis(user, calibration, preclinic_order):

    data = {
        'user': user,
        'calibration': calibration,
        'order': preclinic_order,
        'images': ContentFile(b'CT e SPET files', name='images.zip')
    }

    return PreClinicDosimetryAnalysis.objects.create(**data)


def test_create(preclinic_dosimetry_analysis):
    assert PreClinicDosimetryAnalysis.objects.exists()


def test_create_at(preclinic_dosimetry_analysis):
    assert isinstance(preclinic_dosimetry_analysis.created_at, datetime)


def test_modified_at(preclinic_dosimetry_analysis):
    assert isinstance(preclinic_dosimetry_analysis.modified_at, datetime)


def test_delete_user_must_delete_clinic_dosimetry(user, preclinic_dosimetry_analysis):
    user.delete()
    assert not PreClinicDosimetryAnalysis.objects.exists()


def test_delete_clinic_dosimetry_must_not_delete_user(user, preclinic_dosimetry_analysis):
    preclinic_dosimetry_analysis.delete()
    assert User.objects.exists()


def test_delete_calibration_must_delete_clinic_dosimetry(calibration, preclinic_dosimetry_analysis):
    calibration.delete()
    assert not PreClinicDosimetryAnalysis.objects.exists()


def test_delete_clinic_dosimetry_must_not_delete_calibration(calibration, preclinic_dosimetry_analysis):
    preclinic_dosimetry_analysis.delete()
    assert Calibration.objects.exists()


def test_delete_order_must_delete_clinic_dosimetry(preclinic_order, preclinic_dosimetry_analysis):
    preclinic_order.delete()
    assert not PreClinicDosimetryAnalysis.objects.exists()


def test_delete_clinic_dosimetry_must_not_delete_order(preclinic_order, preclinic_dosimetry_analysis):
    preclinic_dosimetry_analysis.delete()
    assert Order.objects.exists()


def test_clinic_dosimetry_one_to_many_relation(user, calibration, preclinic_order):

    analyis_1 = PreClinicDosimetryAnalysis.objects.create(user=user,
                                                          calibration=calibration,
                                                          order=preclinic_order,
                                                          images=ContentFile(b'CT e SPET files', name='images.zip')
                                                          )

    analyis_2 = PreClinicDosimetryAnalysis.objects.create(user=user,
                                                          calibration=calibration,
                                                          order=preclinic_order,
                                                          images=ContentFile(b'CT e SPET files', name='images.zip')
                                                          )

    assert user.preclinic_dosimetry_analysis.count() == 2

    assert calibration.preclinic_dosimetry_analysis.count() == 2

    assert preclinic_order.preclinic_dosimetry_analysis.count() == 2

    assert analyis_1.user == user
    assert analyis_1.calibration == calibration
    assert analyis_1.order == preclinic_order

    assert analyis_2.user == user
    assert analyis_2.calibration == calibration
    assert analyis_2.order == preclinic_order


def test_default_values(user, calibration, preclinic_order):

    analyis = PreClinicDosimetryAnalysis.objects.create(user=user,
                                                        calibration=calibration,
                                                        order=preclinic_order,
                                                        images=ContentFile(b'CT e SPET files', name='images.zip')
                                                        )

    assert analyis.status == PreClinicDosimetryAnalysis.ANALYZING_INFOS
    assert analyis.active


def test_str(preclinic_dosimetry_analysis):

    analyis = PreClinicDosimetryAnalysis.objects.first()

    infos = analyis._infos()

    clinic = infos['clinic']
    isotope = infos['isotope']
    year = infos['year']

    assert str(analyis) == f'{clinic:04}.{isotope}.{year}/0001-{PreClinicDosimetryAnalysis.CODE}'


def test_status(user, calibration, preclinic_order):

    analysis = PreClinicDosimetryAnalysis(user=user,
                                          calibration=calibration,
                                          order=preclinic_order,
                                          images=ContentFile(b'CT e SPET files', name='images.zip'),
                                          status='AA')

    with pytest.raises(ValidationError):
        analysis.full_clean()
