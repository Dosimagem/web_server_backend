from decimal import Decimal

import pytest

from web_server.service.forms import CreateQuotasForm, DisableSaveFormException
from web_server.service.models import UserQuota


@pytest.fixture
def create_data():
    return {
        'price': '1000.00',
        'amount': 10,
        'service_type': UserQuota.DOSIMETRY_CLINIC,
    }


def test_valid_form(create_data):
    form = CreateQuotasForm(data=create_data)

    assert form.is_valid()

    assert form.cleaned_data['amount'] == 10
    assert form.cleaned_data['price'] == Decimal('1000.00')
    assert form.cleaned_data['service_type'] == UserQuota.DOSIMETRY_CLINIC


def test_invalid_form_negative_amount_number(create_data):

    create_data['amount'] = -10

    form = CreateQuotasForm(data=create_data)

    assert not form.is_valid()

    assert form.errors == {'amount': ['Ensure this value is greater than or equal to 0.']}


def test_invalid_form_amount(create_data):

    create_data['amount'] = '1..0'

    form = CreateQuotasForm(data=create_data)

    assert not form.is_valid()

    assert form.errors == {'amount': ['Enter a whole number.']}


def test_invalid_form_service_type(create_data):

    create_data['service_type'] = 'AAA'

    form = CreateQuotasForm(data=create_data)

    assert not form.is_valid()

    assert form.errors == {'service_type': ['Select a valid choice. AAA is not one of the available choices.']}


def test_invalid_form_price(create_data):

    create_data['price'] = '100.0.0'

    form = CreateQuotasForm(data=create_data)

    assert not form.is_valid()

    assert form.errors == {'price': ['Enter a number.']}


@pytest.mark.django_db
def test_valid_form_save(create_data):

    form = CreateQuotasForm(data=create_data)

    form.full_clean()

    with pytest.raises(DisableSaveFormException):
        form.save()

    assert not UserQuota.objects.exists()
