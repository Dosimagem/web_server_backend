from datetime import datetime

import pytest
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError

from web_server.service.models import UserQuotas

User = get_user_model()


@pytest.fixture
def user_quotas(user):
    return UserQuotas.objects.create(user=user, clinic_dosimetry=10)


def test_quotas_create(user_quotas):
    assert UserQuotas.objects.exists()


def test_quotas_create_at(user_quotas):
    assert isinstance(user_quotas.created_at, datetime)


def test_quotas_modified_at(user_quotas):
    assert isinstance(user_quotas.modified_at, datetime)


def test_quotas_one_to_one_relation(user, user_quotas):
    assert user_quotas.user.id == user.id
    assert user.quotas == user_quotas


def test_delete_user_must_delete_quotes(user, user_quotas):
    user.delete()
    assert not UserQuotas.objects.exists()


def test_delete_quotas_must_not_dele_user(user, user_quotas):
    user_quotas.delete()
    assert User.objects.exists()


def test_quotas_str(user_quotas):
    assert str(user_quotas) == user_quotas.user.profile.name


def test_quotas_default_values(user):
    quotas = UserQuotas.objects.create(user=user)

    assert quotas.clinic_dosimetry== 0


def test_quotas_positive_integer_constraint(user):
    with pytest.raises(IntegrityError):
        UserQuotas.objects.create(user=user, clinic_dosimetry=-1)
