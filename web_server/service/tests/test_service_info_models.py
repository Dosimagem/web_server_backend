from datetime import datetime

import pytest

from django.utils.timezone import now

from web_server.service.models import Info


@pytest.fixture
def info(db):
    return Info.objects.create()


def test_dosimetria(info):
    assert Info.objects.exists()


def test_str(info):
    assert str(info) == 'Info(id=1)'