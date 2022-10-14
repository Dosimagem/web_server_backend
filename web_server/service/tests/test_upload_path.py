from datetime import datetime, timezone

import pytest

from web_server.service.models import (
    _timestamp,
    upload_calibration_to,
    upload_clinic_dosimetry_to,
    upload_preclinic_dosimetry_to,
    upload_report_to,
    upload_segmentation_analysis_to,
)


@pytest.fixture
def datetime_now():
    return datetime(year=2022, month=1, day=1, tzinfo=timezone.utc)


def test_timestamp(datetime_now):
    assert _timestamp(datetime_now) == '16409952000'


def test_upload_name_images_calibration(mocker, first_calibration, datetime_now):

    t = datetime_now
    time_stamp_str = str(t.timestamp()).replace('.', '')

    mocker.patch('web_server.service.models.now', return_value=t)

    id = first_calibration.user.id

    expected = f'{id}/calibration_{time_stamp_str}.zip'

    assert upload_calibration_to(first_calibration, filename='filename.zip') == expected


def test_upload_name_images_clinic_dosinetry_analysis(mocker, clinic_dosimetry, datetime_now):

    t = datetime_now
    time_stamp_str = str(t.timestamp()).replace('.', '')

    mocker.patch('web_server.service.models.now', return_value=t)

    id = clinic_dosimetry.order.user.id

    expected = f'{id}/clinic_dosimetry_{time_stamp_str}.zip'

    assert upload_clinic_dosimetry_to(clinic_dosimetry, filename='filename.zip') == expected


def test_upload_name_images_preclinic_dosinetry_analysis(mocker, preclinic_dosimetry, datetime_now):

    t = datetime_now
    time_stamp_str = str(t.timestamp()).replace('.', '')

    mocker.patch('web_server.service.models.now', return_value=t)

    id = preclinic_dosimetry.order.user.id

    expected = f'{id}/preclinic_dosimetry_{time_stamp_str}.zip'

    assert upload_preclinic_dosimetry_to(preclinic_dosimetry, filename='filename.zip') == expected


def test_upload_name_images_segmentation_analysis(mocker, segmentation_analysis, datetime_now):

    t = datetime_now
    time_stamp_str = str(t.timestamp()).replace('.', '')

    mocker.patch('web_server.service.models.now', return_value=t)

    id = segmentation_analysis.order.user.id

    expected = f'{id}/segmentation_analysis_{time_stamp_str}.zip'

    assert upload_segmentation_analysis_to(segmentation_analysis, filename='filename.zip') == expected


def test_report_name(mocker, clinic_dosimetry, datetime_now):

    t = datetime_now
    time_stamp_str = str(t.timestamp()).replace('.', '')

    mocker.patch('web_server.service.models.now', return_value=t)

    id = clinic_dosimetry.order.user.id

    expected = f'{id}/report_{time_stamp_str}.zip'

    assert upload_report_to(clinic_dosimetry, filename='filename.zip') == expected
