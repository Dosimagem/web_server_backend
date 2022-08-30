from datetime import datetime

import pytest
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError

from web_server.service.models import UserQuota

User = get_user_model()


def test_quotas_create(user_and_quota):
    assert UserQuota.objects.exists()


def test_quotas_create_at(user_and_quota):
    assert isinstance(user_and_quota.created_at, datetime)


def test_quotas_modified_at(user_and_quota):
    assert isinstance(user_and_quota.modified_at, datetime)


def test_delete_user_must_delete_quotes(user, user_and_quota):
    user.delete()
    assert not UserQuota.objects.exists()


def test_delete_quotas_must_not_dele_user(user, user_and_quota):
    user_and_quota.delete()
    assert User.objects.exists()


def test_quotas_str(user_and_quota):
    assert str(user_and_quota) == user_and_quota.user.profile.name


def test_quotas_positive_integer_constraint(user):
    with pytest.raises(IntegrityError):
        UserQuota.objects.create(user=user, amount=-1)


def test_quotas_one_to_many_relation(user, second_user, users_and_quotas):

    assert users_and_quotas[0].user.id == user.id
    assert users_and_quotas[1].user.id == user.id

    assert users_and_quotas[2].user.id == second_user.id

    assert user.quotas.count() == 2
    assert second_user.quotas.count() == 1
