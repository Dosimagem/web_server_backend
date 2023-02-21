from datetime import datetime, timezone

import pytest
from django.utils.text import slugify

from web_server.signature.models import upload_to

DATE_STR = '011222020342'


@pytest.fixture
def datetime_now():
    return datetime(year=2022, month=12, day=1, hour=2, minute=3, second=42, tzinfo=timezone.utc)


def test_bill_name(mocker, user_signature, datetime_now):

    t = datetime_now

    mocker.patch('web_server.signature.models.now', return_value=t)

    id = user_signature.user.pk

    expected = f'{id}/signatures/{slugify(user_signature.plan)}/bill_{DATE_STR}.zip'

    assert upload_to(user_signature, filename='filename.zip') == expected
