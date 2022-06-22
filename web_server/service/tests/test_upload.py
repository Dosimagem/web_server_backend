from unittest import mock
from datetime import datetime

import pytest

from web_server.service.models import upload_to, _normalize_email


@pytest.fixture
def datetime_now():
    t = datetime(year=2022, month=1, day=1)

    date = f'{t:%Y/%m/%d}'
    time = f'{t:%H%M%S}'

    return t, date, time


def test_normalize_email(user):
    assert 'test_email_com' == _normalize_email(user.email)





@mock.patch('web_server.service.models.now')
def test_upload_name_to_info(mock, info, datetime_now):
    t, date, time =  datetime_now

    mock.return_value = t

    user = _normalize_email(info.order.requester.email)

    assert upload_to(info, 'filename.zip') == f'{user}/images/{date}/images_{time}.zip'


@mock.patch('web_server.service.models.now')
def test_upload_name_to_service(mock, order, datetime_now):
    t, date, time =  datetime_now

    mock.return_value = t
    user = _normalize_email(order.requester.email)

    assert upload_to(order, 'filename.pdf') == f'{user}/report/{date}/report_{time}.pdf'
