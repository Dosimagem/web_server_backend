from decimal import Decimal
from datetime import datetime

import pytest

from django.forms import ValidationError

from web_server.service.models import SegmentationOrder, Service
from web_server.core.models import CostumUser as User


def test_type_services(segmentantion_order):
    '''
    There nust be only one entry in the db
    '''
    assert SegmentationOrder.objects.exists()


def test_delete_order_keep_user(segmentantion_order, user):
    '''
    Deleting the segmentantion_order should not delete the user
    '''
    segmentantion_order.delete()
    assert not SegmentationOrder.objects.exists()
    assert User.objects.exists()


def test_delete_user_delete_order(segmentantion_order, user):
    '''
    Deleting the user should delete the segmentantion_order
    '''
    user.delete()
    assert not User.objects.exists()
    assert not SegmentationOrder.objects.exists()


def test_delete_order_keep_service(segmentantion_order, services):
    '''
    Deleting the segmentantion_order should not delete the service
    '''
    n_services = Service.objects.all().count()

    segmentantion_order.delete()
    assert not SegmentationOrder.objects.exists()
    assert Service.objects.all().count() == n_services


def test_delete_service_delete_order(segmentantion_order, segmentantion_service):
    '''
    Deleting the service should delete the segmentantion_order
    '''
    n_services = Service.objects.all().count()

    segmentantion_service.delete()
    assert not SegmentationOrder.objects.exists()
    assert Service.objects.all().count() == n_services - 1


def test_total_price(segmentantion_order):
    '''
    The total price must be the quantity times the unit price of the service
    '''
    assert segmentantion_order.total_price == Decimal('2000.50')


def test_order_create_at(segmentantion_order):
    assert isinstance(segmentantion_order.created_at, datetime)


def test_order_modified_at(segmentantion_order):
    assert isinstance(segmentantion_order.modified_at, datetime)


def test_order_status(segmentantion_order):
    o = SegmentationOrder.objects.all().first()
    assert o.status == SegmentationOrder.PROCESSING


def test_order_choices(segmentantion_order, services):
    '''
    Status only must have APG, APR, PRC and CON options
    '''
    with pytest.raises(ValidationError):
        segmentantion_order.status = 'CDA'
        segmentantion_order.full_clean()


def test_str(segmentantion_order):
    assert str(segmentantion_order) == 'Segmentantion (id=1)'
