from decimal import Decimal
from datetime import datetime

import pytest

from django.forms import ValidationError
from web_server.conftest import DATETIME_TIMEZONE

from web_server.service.models import DosimetryOrder, Service
from web_server.core.models import CustomUser as User


def test_type_services(dosimetry_clinical_order):
    '''
    There nust be only one entry in the db
    '''
    assert DosimetryOrder.objects.exists()


def test_delete_order_keep_user(dosimetry_clinical_order, user):
    '''
    Deleting the dosimetry_clinical_order should not delete the user
    '''
    dosimetry_clinical_order.delete()
    assert not DosimetryOrder.objects.exists()
    assert User.objects.exists()


def test_delete_user_delete_order(dosimetry_clinical_order, user):
    '''
    Deleting the user should delete the dosimetry_clinical_order
    '''
    user.delete()
    assert not User.objects.exists()
    assert not DosimetryOrder.objects.exists()


def test_delete_order_keep_service(dosimetry_clinical_order, services):
    '''
    Deleting the dosimetry_clinical_order should not delete the service
    '''
    n_services = Service.objects.all().count()
    dosimetry_clinical_order.delete()
    assert not DosimetryOrder.objects.exists()
    assert Service.objects.all().count() == n_services


def test_delete_service_delete_order(dosimetry_clinical_order, dosimetry_clinical_service):
    '''
    Deleting the service should delete the dosimetry_clinical_order
    '''
    n_services = Service.objects.all().count()
    dosimetry_clinical_service.delete()
    assert not DosimetryOrder.objects.exists()
    assert Service.objects.all().count() == n_services - 1


def test_total_price(dosimetry_clinical_order):
    '''
    The total price must be the quantity times the unit price of the service
    '''
    assert dosimetry_clinical_order.total_price == Decimal('3710.42')


def test_order_create_at(dosimetry_clinical_order):
    assert isinstance(dosimetry_clinical_order.created_at, datetime)


def test_order_modified_at(dosimetry_clinical_order):
    assert isinstance(dosimetry_clinical_order.modified_at, datetime)


def test_order_status(dosimetry_clinical_order):
    o = DosimetryOrder.objects.all().first()
    assert o.status == DosimetryOrder.PROCESSING


def test_order_choices(dosimetry_clinical_order):
    '''
    Status only must have APG, APR, PRC and CON options
    '''
    with pytest.raises(ValidationError):
        dosimetry_clinical_order.status = 'CDA'
        dosimetry_clinical_order.full_clean()


def test_dosimetry_order_choices(dosimetry_clinical_order):
    '''
    Status only must have C and P options
    '''
    with pytest.raises(ValidationError):
        dosimetry_clinical_order.type = 'D'
        dosimetry_clinical_order.full_clean()


def test_dosimetry_order_set_type(dosimetry_clinical_order):
    '''
    Test that the type was correctly deduced from the service name
    '''
    assert dosimetry_clinical_order.type == DosimetryOrder.CLINICAL


def test_str(dosimetry_clinical_order):
    assert str(dosimetry_clinical_order) == 'Clinical Dosimetry (id=1)'


def test_default_status_is_awaiting_payment(user, dosimetry_clinical_service):

    order = DosimetryOrder.objects.create(requester=user,
                                          service=dosimetry_clinical_service,
                                          amount=2,
                                          camera_factor=10.0,
                                          radionuclide='Lu-177',
                                          injected_activity=50.0,
                                          injection_datetime=DATETIME_TIMEZONE,
                                          images='images.zip')

    assert order.status == DosimetryOrder.AWAITING_PAYMENT
