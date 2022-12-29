from datetime import datetime

import pytest
from django.db import IntegrityError

from web_server.signature.models import Benefit


def test_create(benefit):
    assert Benefit.objects.exists()


def test_create_at_and_modified_at(benefit):
    assert isinstance(benefit.created_at, datetime)
    assert isinstance(benefit.modified_at, datetime)


def test_str(benefit):
    assert str(benefit) == benefit.name


def test_constrain_name(benefit):
    with pytest.raises(IntegrityError):
        Benefit.objects.create(name='RSV', uri='/dashboard/my-signatures/Benefit/calculator')
