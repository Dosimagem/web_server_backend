from datetime import datetime, timezone

import pytest
from django.utils.text import slugify

from web_server.service.models import (
    _timestamp,
    upload_calibration_to,
    upload_clinic_dosimetry_to,
    upload_payment_slip_to,
    upload_preclinic_dosimetry_to,
    upload_report_to,
    upload_segmentation_analysis_to,
)

DATE_STR = '011222020342'


@pytest.fixture
def datetime_now():
    return datetime(year=2022, month=12, day=1, hour=2, minute=3, second=42, tzinfo=timezone.utc)


def test_timestamp(datetime_now):
    assert DATE_STR == _timestamp(datetime_now)


def test_upload_name_images_calibration(mocker, first_calibration, datetime_now):

    t = datetime_now

    mocker.patch('web_server.service.models.now', return_value=t)

    id = first_calibration.user.id

    expected = f'{id}/calibration_{DATE_STR}.zip'

    assert upload_calibration_to(first_calibration, filename='filename.zip') == expected


def test_upload_name_images_clinic_dosinetry_analysis(mocker, clinic_dosimetry, datetime_now):

    t = datetime_now

    mocker.patch('web_server.service.models.now', return_value=t)

    id = clinic_dosimetry.order.user.id
    order_code = slugify(clinic_dosimetry.order.code)
    number = clinic_dosimetry.order.quantity_of_analyzes - clinic_dosimetry.order.remaining_of_analyzes + 1

    expected = f'{id}/{order_code}/{number}/clinic_dosimetry_{DATE_STR}.zip'

    assert upload_clinic_dosimetry_to(clinic_dosimetry, filename='filename.zip') == expected


def test_upload_name_images_preclinic_dosinetry_analysis(mocker, preclinic_dosimetry, datetime_now):

    t = datetime_now

    mocker.patch('web_server.service.models.now', return_value=t)

    id = preclinic_dosimetry.order.user.id
    order_code = slugify(preclinic_dosimetry.order.code)
    number = preclinic_dosimetry.order.quantity_of_analyzes - preclinic_dosimetry.order.remaining_of_analyzes + 1

    expected = f'{id}/{order_code}/{number}/preclinic_dosimetry_{DATE_STR}.zip'

    assert upload_preclinic_dosimetry_to(preclinic_dosimetry, filename='filename.zip') == expected


def test_upload_name_images_segmentation_analysis(mocker, segmentation_analysis, datetime_now):

    t = datetime_now

    mocker.patch('web_server.service.models.now', return_value=t)

    id = segmentation_analysis.order.user.id
    order_code = slugify(segmentation_analysis.order.code)
    number = segmentation_analysis.order.quantity_of_analyzes - segmentation_analysis.order.remaining_of_analyzes + 1

    expected = f'{id}/{order_code}/{number}/segmentation_analysis_{DATE_STR}.zip'

    assert upload_segmentation_analysis_to(segmentation_analysis, filename='filename.zip') == expected


def test_report_name(mocker, clinic_dosimetry, datetime_now):

    t = datetime_now

    mocker.patch('web_server.service.models.now', return_value=t)

    id = clinic_dosimetry.order.user.id
    order_code = slugify(clinic_dosimetry.order.code)
    number = clinic_dosimetry.order.quantity_of_analyzes - clinic_dosimetry.order.remaining_of_analyzes + 1

    expected = f'{id}/{order_code}/{number}/report_{DATE_STR}.zip'

    assert upload_report_to(clinic_dosimetry, filename='filename.zip') == expected


def test_payment_slip_name(mocker, clinic_order, datetime_now):

    t = datetime_now

    mocker.patch('web_server.service.models.now', return_value=t)

    id = clinic_order.user.id
    order_code = slugify(clinic_order.code)

    expected = f'{id}/{order_code}/payment_slip_{DATE_STR}.pdf'

    assert upload_payment_slip_to(clinic_order, filename='filename.pdf') == expected
