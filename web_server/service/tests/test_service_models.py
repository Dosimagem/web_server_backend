from datetime import datetime
from decimal import Decimal

import pytest

from web_server.service.models import Service


def test_type_services(services):
    '''
    There must be entries in the db
    '''
    assert Service.objects.exists()


@pytest.mark.parametrize('index, price', [
    (0, Decimal('1855.21')),
    (1, Decimal('2000.50')),
    (2, Decimal('4000.55')),
])
def test_get_price(index, price, services):
    '''
    There must be a decimal number
    '''
    assert services[index].unit_price == price


def test_service_create_at(services):
    for s in services:
        assert isinstance(s.created_at, datetime)


def test_service_modified_at(services):
    for s in services:
        assert isinstance(s.modified_at, datetime)


@pytest.mark.parametrize('index, name', [
    (0, 'Dosimetria Clinica'),
    (1, 'Segmentação'),
    (2, 'Modelagem Computacinal'),
])
def test_str(index, name, services):
    assert str(services[index]) == name
