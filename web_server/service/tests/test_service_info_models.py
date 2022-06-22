from datetime import datetime

import pytest

from django.utils.timezone import now

from web_server.service.models import Info


def test_dosimetria(info):
    assert Info.objects.exists()


def test_str(info):
    assert str(info) == f'Infos {info.order.service.name}'
