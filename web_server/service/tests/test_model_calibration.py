from datetime import datetime

from django.contrib.auth import get_user_model

from web_server.service.models import Calibration, Isotope


User = get_user_model()


def test_create_calibration(calibration):
    assert Calibration.objects.exists()


def test_calibration_create_at(calibration):
    assert isinstance(calibration.created_at, datetime)


def test_calibration_modified_at(calibration):
    assert isinstance(calibration.modified_at, datetime)


def test_delete_calibration_must_not_delete_user_and_isotope(calibration):

    calibration.delete()

    assert not Calibration.objects.exists()
    assert User.objects.exists()
    assert Isotope.objects.exists()


def test_delete_isotope_must_be_delete_calibration(calibration, lu_177):

    lu_177.delete()

    assert not Calibration.objects.exists()
    assert not Isotope.objects.exists()


def test_delete_user_must_be_delete_calibration(calibration, user):

    user.delete()

    assert not Calibration.objects.exists()
    assert not User.objects.exists()


def test_str_(calibration):

    assert str(calibration) == calibration.calibration_name
