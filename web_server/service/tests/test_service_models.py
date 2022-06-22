from datetime import datetime
from decimal import Decimal

import pytest

from web_server.service.models import Service


def test_type_services(service):
    '''
    There nust be only one entry in the db
    '''
    assert Service.objects.exists()


def test_get_price(service):
    '''
    There must be a decimal number
    '''
    assert service.unit_price == Decimal('1855.21')


def test_service_create_at(service):
    assert isinstance(service.created_at, datetime)


def test_service_modified_at(service):
    assert isinstance(service.modified_at, datetime)


def test_str(service):
    assert str(service) == 'Dosimetria Clinica'
