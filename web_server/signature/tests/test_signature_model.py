from datetime import datetime
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from web_server.signature.models import Signature

pytestmark = pytest.mark.django_db


def test_create(user_signature):
    assert Signature.objects.exists()


def test_create_at_and_modified_at(user_signature):
    assert isinstance(user_signature.created_at, datetime)
    assert isinstance(user_signature.modified_at, datetime)


def test_str(user_signature):
    assert str(user_signature) == user_signature.plan


def test_signatures_Benefit_many_to_many_relation(user_signature, user_other_signature, benefit_list):

    assert user_signature.benefits.count() == 3
    assert user_other_signature.benefits.count() == 1

    b1, b2, b3 = benefit_list

    assert b1.signatures.count() == 2
    assert b2.signatures.count() == 1
    assert b3.signatures.count() == 1

    assert set(b1.signatures.all()) == set([user_other_signature, user_signature])
    assert b2.signatures.first() == user_signature
    assert b3.signatures.first() == user_signature


def test_signatures_user_one_to_many_relation(user_signature, user_other_signature, user):

    assert user_signature.user == user
    assert user_other_signature.user == user

    assert user.signatures.count() == 2

    assert set(user.signatures.all()) == set([user_signature, user_other_signature])


def test_detault_values(user_signature):

    assert user_signature.hired_period_initial is None
    assert user_signature.hired_period_end is None
    assert user_signature.test_period_initial is None
    assert user_signature.test_period_end is None
    assert user_signature.activated is False
    assert user_signature.modality == Signature.Modality.YEARLY
    assert user_signature.discount == Decimal('0.00')
    # assert signature1.bill_file == ''


def test_test_hired_range_period(user):

    sig = Signature(
        user=user,
        plan='Pacote Dosimagem Anual',
        price='600.00',
        hired_period_initial=datetime(2001, 1, 2),
        hired_period_end=datetime(2002, 1, 2),
    )

    assert sig.hired_period_initial == datetime(2001, 1, 2)
    assert sig.hired_period_end == datetime(2002, 1, 2)

    sig = Signature(
        user=user,
        plan='Pacote Dosimagem Anual',
        price='600.00',
        test_period_initial=datetime(2001, 1, 2),
        test_period_end=datetime(2001, 2, 2),
    )

    assert sig.test_period_initial == datetime(2001, 1, 2)
    assert sig.test_period_end == datetime(2001, 2, 2)


def test_end_must_be_after_init(user):

    sig = Signature(
        user=user,
        plan='Pacote Dosimagem Anual',
        price='600.00',
        hired_period_initial=datetime(2002, 1, 2),
        hired_period_end=datetime(2001, 1, 2),
    )

    with pytest.raises(ValidationError):
        sig.full_clean()

    sig = Signature(
        plan='Pacote Dosimagem Anual',
        price='600.00',
        test_period_initial=datetime(2002, 1, 2),
        test_period_end=datetime(2001, 1, 2),
    )

    with pytest.raises(ValidationError):
        sig.full_clean()


def test_hired_period_info(user):

    sig = Signature(
        user=user,
        plan='Pacote Dosimagem Anual',
        price='600.00',
        hired_period_initial=datetime(2001, 1, 2),
        hired_period_end=datetime(2002, 1, 2),
    )

    assert sig.hired_period == {'initial': '2001-01-02', 'end': '2002-01-02'}

    sig = Signature(
        plan='Pacote Dosimagem Anual',
        price='600.00',
    )

    assert sig.hired_period is None


def test_test_period_info(user):

    sig = Signature(
        user=user,
        plan='Pacote Dosimagem Anual',
        price='600.00',
        test_period_initial=datetime(2001, 1, 2),
        test_period_end=datetime(2002, 1, 2),
    )

    assert sig.test_period == {'initial': '2001-01-02', 'end': '2002-01-02'}

    sig = Signature(
        plan='Pacote Dosimagem Anual',
        price='600.00',
    )

    assert sig.test_period is None
