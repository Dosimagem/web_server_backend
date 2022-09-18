from datetime import datetime, timezone

import pytest

from web_server.service.models import upload_calibration_to, _timestamp


@pytest.fixture
def datetime_now():
    return datetime(year=2022, month=1, day=1, tzinfo=timezone.utc)


def test_timestamp(datetime_now):
    assert _timestamp(datetime_now) == '16409952000'


def test_upload_name_images_calibration(mocker, user, calibration, datetime_now):

    t = datetime_now
    time_stamp_str = str(t.timestamp()).replace('.', '')

    mocker.patch('web_server.service.models.now', return_value=t)

    id = calibration.user.id

    expected = f'{id}/calibration_{time_stamp_str}.zip'

    assert upload_calibration_to(calibration, filename='filename.zip') == expected
