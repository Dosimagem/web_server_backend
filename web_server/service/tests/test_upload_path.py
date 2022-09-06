from unittest import mock
from datetime import datetime

import pytest
from django.utils.text import slugify

from web_server.service.models import upload_calibration_to, _timestamp


@pytest.fixture
def datetime_now():
    return datetime(year=2022, month=1, day=1)


def test_timestamp(datetime_now):
    assert _timestamp(datetime_now) == '16409952000'


@mock.patch('web_server.service.models.now')
def test_upload_name_images_calibration(mock, user, calibration, datetime_now):
    t = datetime_now
    time_stamp_str = str(t.timestamp()).replace('.', '')

    mock.return_value = t
    slug = slugify(calibration.calibration_name)

    expected = f'{user.id}/calibrations/{slug}/calibration_{time_stamp_str}.zip'

    assert upload_calibration_to(calibration, filename='filename.zip') == expected


# @mock.patch('web_server.service.models.now')
# def test_upload_name_report_dosimetry_order(mock, dosimetry_clinical_order, datetime_now):
#     t, date, time = datetime_now

#     mock.return_value = t
#     user = _normalize_email(dosimetry_clinical_order.requester.email)

#     assert upload_report_to(dosimetry_clinical_order, 'filename.pdf') == f'{user}/report/{date}/report_{time}.pdf'


# @mock.patch('web_server.service.models.now')
# def test_upload_name_images_segmentantion_order(mock, segmentantion_order, datetime_now):
#     t, date, time = datetime_now

#     mock.return_value = t

#     user = _normalize_email(segmentantion_order.requester.email)

#     assert upload_img_to(segmentantion_order, filename='filename.zip') == f'{user}/images/{date}/images_{time}.zip'


# @mock.patch('web_server.service.models.now')
# def test_upload_name_report_segmentantion_order(mock, segmentantion_order, datetime_now):
#     t, date, time = datetime_now

#     mock.return_value = t
#     user = _normalize_email(segmentantion_order.requester.email)

#     assert upload_report_to(segmentantion_order, 'filename.pdf') == f'{user}/report/{date}/report_{time}.pdf'
