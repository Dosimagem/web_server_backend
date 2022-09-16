from unittest import mock
from datetime import datetime, timezone

import pytest
from django.utils.text import slugify

from web_server.service.models import upload_calibration_to, _timestamp


@pytest.fixture
def datetime_now():
    return datetime(year=2022, month=1, day=1, tzinfo=timezone.utc)


def test_timestamp(datetime_now):
    assert _timestamp(datetime_now) == '16409952000'


@mock.patch('web_server.service.models.now')
def test_upload_name_images_calibration(mock, user, calibration, datetime_now):
    t = datetime_now
    time_stamp_str = str(t.timestamp()).replace('.', '')

    mock.return_value = t
    slug_calibration_name = slugify(calibration.calibration_name)
    id = calibration.user.id

    expected = f'{id}/calibrations/{slug_calibration_name}_{time_stamp_str}.zip'

    assert upload_calibration_to(calibration, filename='filename.zip') == expected
