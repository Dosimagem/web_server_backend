from decimal import Decimal
from datetime import datetime

import pytest

from django.forms import ValidationError

from web_server.service.models import DosimetryOrder, Service
from web_server.core.models import CostumUser as User


def test_type_services(dosimetry_order):
    '''
    There nust be only one entry in the db
    '''
    assert DosimetryOrder.objects.exists()


def test_delete_order_keep_user(dosimetry_order, user):
    '''
    Deleting the dosimetry_order should not delete the user
    '''
    dosimetry_order.delete()
    assert not DosimetryOrder.objects.exists()
    assert User.objects.exists()


def test_delete_user_delete_order(dosimetry_order, user):
    '''
    Deleting the user should delete the dosimetry_order
    '''
    user.delete()
    assert not User.objects.exists()
    assert not DosimetryOrder.objects.exists()


def test_delete_order_keep_service(dosimetry_order, services):
    '''
    Deleting the dosimetry_order should not delete the service
    '''
    n_services = Service.objects.all().count()
    dosimetry_order.delete()
    assert not DosimetryOrder.objects.exists()
    assert Service.objects.all().count() == n_services


def test_delete_service_delete_order(dosimetry_order, dosimetry_service):
    '''
    Deleting the service should delete the dosimetry_order
    '''
    n_services = Service.objects.all().count()
    dosimetry_service.delete()
    assert not DosimetryOrder.objects.exists()
    assert Service.objects.all().count() == n_services - 1


def test_total_price(dosimetry_order):
    '''
    The total price must be the quantity times the unit price of the service
    '''
    assert dosimetry_order.total_price == Decimal('3710.42')


def test_order_create_at(dosimetry_order):
    assert isinstance(dosimetry_order.created_at, datetime)


def test_order_modified_at(dosimetry_order):
    assert isinstance(dosimetry_order.modified_at, datetime)


def test_order_status(dosimetry_order):
    o = DosimetryOrder.objects.all().first()
    assert o.status == DosimetryOrder.PROCESSING


def test_order_choices(dosimetry_order):
    '''
    Status only must have APG, APR, PRC and CON options
    '''
    with pytest.raises(ValidationError):
        dosimetry_order.status = 'CDA'
        dosimetry_order.full_clean()


def test_dosimetry_order_choices(dosimetry_order):
    '''
    Status only must have C and P options
    '''
    with pytest.raises(ValidationError):
        dosimetry_order.type = 'D'
        dosimetry_order.full_clean()


def test_str(dosimetry_order):
    assert str(dosimetry_order) == 'Clinical Dosimetry (id=1)'
