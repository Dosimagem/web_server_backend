from datetime import datetime
from decimal import Decimal

import pytest

from web_server.service.models import Service


@pytest.fixture
def create_service(db):
    return Service.objects.create(name='Dosimetria Clinica',
                                  description='Serviço de dosimentria',
                                  unit_price=Decimal('1855.21'))


def test_type_services(create_service):
    '''
    There nust be only one entry in the db
    '''
    assert Service.objects.exists()


def test_get_price(create_service):
    '''
    There must be a decimal number
    '''
    assert create_service.unit_price == Decimal('1855.21')


def test_service_create_at(create_service):
    assert isinstance(create_service.created_at, datetime)


def test_service_modified_at(create_service):
    assert isinstance(create_service.modified_at, datetime)


def test_str(create_service):
    assert str(create_service) == 'Dosimetria Clinica'
