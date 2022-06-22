from datetime import datetime
from decimal import Decimal
from django.forms import ValidationError

import pytest

from web_server.service.models import Info, Order, Service
from web_server.core.models import CostumUser as User


def test_type_services(order):
    '''
    There nust be only one entry in the db
    '''
    assert Order.objects.exists()


def test_delete_order_keep_user(order, user):
    '''
    Deleting the order should not delete the user
    '''
    order.delete()
    assert not Order.objects.exists()
    assert User.objects.exists()


def test_delete_user_delete_order(order, user):
    '''
    Deleting the user should delete the order
    '''
    user.delete()
    assert not User.objects.exists()
    assert not Order.objects.exists()


def test_delete_order_keep_service(order, service):
    '''
    Deleting the order should not delete the service
    '''
    order.delete()
    assert not Order.objects.exists()
    assert Service.objects.exists()


def test_delete_service_delete_order(order, service):
    '''
    Deleting the service should delete the order
    '''
    service.delete()
    assert not Order.objects.exists()
    assert not Service.objects.exists()


def test_delete_order_delete_info(order, info):
    '''
    Deleting the order should delete the info
    '''
    order.delete()
    assert not Order.objects.exists()
    assert not Info.objects.exists()


def test_delete_info_delete_order(order, info):
    '''
    Deleting the service should delete the order
    '''
    info.delete()
    assert not Order.objects.exists()
    assert not Info.objects.exists()


def test_total_price(order):
    '''
    The total price must be the quantity times the unit price of the service
    '''
    assert order.total_price == Decimal('3710.42')


def test_order_create_at(order):
    assert isinstance(order.created_at, datetime)


def test_order_modified_at(order):
    assert isinstance(order.modified_at, datetime)


def test_order_status(order):
    o = Order.objects.all().first()
    assert o.status == Order.PROCESSING


def test_order_choise(user, service, info):
    '''
    Status only must have APG, APR, PRC and CON options
    '''
    with pytest.raises(ValidationError):
        Order.objects.create(requester=user, service=service, info=info, amount=2, status='CAD').full_clean()


def test_str(order):
    assert str(order) == 'Order(id=1)'  # TODO: Temporario
