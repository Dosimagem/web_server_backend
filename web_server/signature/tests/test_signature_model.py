from datetime import datetime
from decimal import Decimal

import pytest
from django.db import IntegrityError
from django.core.exceptions import ValidationError

from web_server.signature.models import Signature, Benefits


@pytest.fixture
def benefits_list(db):
    b1 = Benefits(name='B1', uri='/benefits/B1')
    b2 = Benefits(name='B2', uri='/benefits/B2')
    b3 = Benefits(name='B3', uri='/benefits/B3')
    return Benefits.objects.bulk_create([b1, b2, b3])

@pytest.fixture
def signature1(user, benefits_list):

    sig = Signature.objects.create(
        name='Pacote Dosimagem mensal',
        price='60.00'
    )

    sig.users.add(user)
    sig.benefits.add(*benefits_list)

    return sig


@pytest.fixture
def signature2(user, second_user, benefits_list):

    sig = Signature.objects.create(
        name='Pacote Dosimagem Anual',
        price='600.00'
    )

    sig.users.add(user, second_user)
    sig.benefits.add(benefits_list[0])

    return sig


def test_create(signature1):
    assert Signature.objects.exists()


def test_create_at_and_modified_at(signature1):
    assert isinstance(signature1.created_at, datetime)
    assert isinstance(signature1.modified_at, datetime)


def test_str(signature1):
    assert str(signature1) == signature1.name

def test_signatures_benefits_many_to_many_relation(signature1, signature2, benefits_list):

    assert signature1.benefits.count() == 3
    assert signature2.benefits.count() == 1

    b1, b2, b3 = benefits_list

    assert b1.signatures.count() == 2
    assert b2.signatures.count() == 1
    assert b3.signatures.count() == 1

    assert set(b1.signatures.all()) == set([signature2, signature1])
    assert b2.signatures.first() == signature1
    assert b3.signatures.first() == signature1


def test_signatures_user_many_to_many_relation(signature1, signature2, user, second_user):

    assert signature1.users.count() == 1
    assert signature2.users.count() == 2

    assert user.signatures.count() == 2
    assert second_user.signatures.count() == 1

    assert set(user.signatures.all()) == set([signature2, signature1])
    assert second_user.signatures.first() == signature2


def test_detault_values(signature1):

    assert signature1.hired_period_init == None
    assert signature1.hired_period_end == None
    assert signature1.test_period_init == None
    assert signature1.test_period_end == None
    assert signature1.activated is False
    # assert signature1.bill_file == ''


def test_test_hired_range_period(db):

    sig = Signature(
        name='Pacote Dosimagem Anual',
        price='600.00',
        hired_period_init=datetime(2001, 1, 2),
        hired_period_end=datetime(2002, 1, 2),
    )

    assert sig.hired_period_init == datetime(2001, 1, 2)
    assert sig.hired_period_end == datetime(2002, 1, 2)

    sig = Signature(
        name='Pacote Dosimagem Anual',
        price='600.00',
        test_period_init=datetime(2001, 1, 2),
        test_period_end=datetime(2001, 2, 2),
    )

    assert sig.test_period_init == datetime(2001, 1, 2)
    assert sig.test_period_end == datetime(2001, 2, 2)


def test_end_must_be_after_init(db):

    sig = Signature(
        name='Pacote Dosimagem Anual',
        price='600.00',
        hired_period_init=datetime(2002, 1, 2),
        hired_period_end=datetime(2001, 1, 2),
    )

    with pytest.raises(ValidationError):
        sig.full_clean()

    sig = Signature(
        name='Pacote Dosimagem Anual',
        price='600.00',
        test_period_init=datetime(2002, 1, 2),
        test_period_end=datetime(2001, 1, 2),
    )

    with pytest.raises(ValidationError):
        sig.full_clean()