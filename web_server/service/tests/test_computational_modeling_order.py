from decimal import Decimal
from datetime import datetime

import pytest

from django.forms import ValidationError

from web_server.service.models import ComputationalModelOrder, Service
from web_server.core.models import CustomUser as User


def test_type_services(computational_modeling):
    '''
    There nust be only one entry in the db
    '''
    assert ComputationalModelOrder.objects.exists()


def test_delete_order_keep_user(computational_modeling, user):
    '''
    Deleting the computational_modeling should not delete the user
    '''
    computational_modeling.delete()
    assert not ComputationalModelOrder.objects.exists()
    assert User.objects.exists()


def test_delete_user_delete_order(computational_modeling, user):
    '''
    Deleting the user should delete the computational_modeling
    '''
    user.delete()
    assert not User.objects.exists()
    assert not ComputationalModelOrder.objects.exists()


def test_delete_order_keep_service(computational_modeling, services):
    '''
    Deleting the computational_modeling should not delete the service
    '''
    n_services = Service.objects.all().count()
    computational_modeling.delete()
    assert not ComputationalModelOrder.objects.exists()
    assert Service.objects.all().count() == n_services


def test_delete_service_delete_order(computational_modeling, computational_modeling_service):
    '''
    Deleting the service should delete the computational_modeling
    '''
    n_services = Service.objects.all().count()
    computational_modeling_service.delete()
    assert not ComputationalModelOrder.objects.exists()
    assert Service.objects.all().count() == n_services - 1


def test_total_price(computational_modeling):
    '''
    The total price must be the quantity times the unit price of the service
    '''
    assert computational_modeling.total_price == Decimal('12001.65')


def test_order_create_at(computational_modeling):
    assert isinstance(computational_modeling.created_at, datetime)


def test_order_modified_at(computational_modeling):
    assert isinstance(computational_modeling.modified_at, datetime)


def test_order_status(computational_modeling):
    o = ComputationalModelOrder.objects.all().first()
    assert o.status == ComputationalModelOrder.PROCESSING


def test_order_choices(computational_modeling):
    '''
    Status only must have APG, APR, PRC and CON options
    '''
    with pytest.raises(ValidationError):
        computational_modeling.status = 'CDA'
        computational_modeling.full_clean()


def test_computational_modeling_equipment_specification_choices(computational_modeling):
    '''
    Equipment specification only must have C and S options
    '''
    with pytest.raises(ValidationError):
        computational_modeling.equipment_specification = 'D'
        computational_modeling.full_clean()


def test_str(computational_modeling):
    assert str(computational_modeling) == 'Computational Modeling (id=1)'
