from datetime import datetime
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError

from web_server.service.models import UserQuota

User = get_user_model()


@pytest.fixture
def two_users_quotas(user, second_user):
    '''
    UserQuota Table:

    ID_USER  Type               Number    Value   Status Payment
    1        Dosimetry Clinic     10     10.000   Confirmed
    1        Dosimetry Preclinic   5      5.000   Analysis
    2        Dosimetry Clinic      3      3.000   Confimed
    '''

    UserQuota.objects.create(user=user,
        amount=10,
        service_type=UserQuota.DOSIMETRY_CLINIC,
        price=Decimal('10000.00'),
        status_payment=UserQuota.CONFIRMED,
        )

    UserQuota.objects.create(user=user,
        amount=5,
        service_type=UserQuota.DOSIMETRY_PRECLINIC,
        price=Decimal('5000.00'),
        status_payment=UserQuota.ANALYSIS,
        )

    UserQuota.objects.create(user=second_user,
        amount=3,
        service_type=UserQuota.DOSIMETRY_PRECLINIC,
        price=Decimal('3000.00'),
        status_payment=UserQuota.ANALYSIS,
        )

    return list(UserQuota.objects.all())


def test_quotas_create(user_quotas):
    assert UserQuota.objects.exists()


def test_quotas_create_at(user_quotas):
    assert isinstance(user_quotas.created_at, datetime)


def test_quotas_modified_at(user_quotas):
    assert isinstance(user_quotas.modified_at, datetime)


def test_delete_user_must_delete_quotes(user, user_quotas):
    user.delete()
    assert not UserQuota.objects.exists()


def test_delete_quotas_must_not_dele_user(user, user_quotas):
    user_quotas.delete()
    assert User.objects.exists()


def test_quotas_str(user_quotas):
    assert str(user_quotas) == user_quotas.user.profile.name


def test_quotas_positive_integer_constraint(user):
    with pytest.raises(IntegrityError):
        UserQuota.objects.create(user=user, amount=-1)


def test_quotas_one_to_many_relation(user, second_user, two_users_quotas):

    assert two_users_quotas[0].user.id == user.id
    assert two_users_quotas[1].user.id == user.id

    assert two_users_quotas[2].user.id == second_user.id

    assert user.quotas.count() == 2
    assert second_user.quotas.count() == 1
