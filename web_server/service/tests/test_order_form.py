from decimal import Decimal

from django.utils.translation import gettext as _

from web_server.service.forms import CreateOrderForm
from web_server.service.models import Order


def test_valid_form(create_order_data):

    form = CreateOrderForm(data=create_order_data)

    assert form.is_valid()
    assert form.cleaned_data['quantity_of_analyzes'] == 10
    assert form.cleaned_data['remaining_of_analyzes'] == 10
    assert form.cleaned_data['price'] == Decimal('1000.00')
    assert form.cleaned_data['service_name'] == Order.DOSIMETRY_CLINIC


def test_invalid_form_negative_quantity_of_analyzes(create_order_data):

    create_order_data['quantity_of_analyzes'] = -10

    form = CreateOrderForm(data=create_order_data)

    assert not form.is_valid()

    msg = _('Ensure this value is greater than or equal to %(limit_value)s.')

    msg = msg % {'limit_value': 0}

    assert form.errors == {'quantity_of_analyzes': [msg]}


def test_invalid_form_quantity_of_analyzes(create_order_data):

    create_order_data['quantity_of_analyzes'] = '1..0'

    form = CreateOrderForm(data=create_order_data)

    assert not form.is_valid()

    assert form.errors == {'quantity_of_analyzes': [_('Enter a whole number.')]}


def test_invalid_form_remaining_of_analyzes_must_be_lower_that_quantity_of_analyzes(create_order_data):

    create_order_data['quantity_of_analyzes'] = '1'
    create_order_data['remaining_of_analyzes'] = '2'

    form = CreateOrderForm(data=create_order_data)

    assert not form.is_valid()

    assert form.errors == {'remaining_of_analyzes': [_('Must be lower with the field quantity of analyzes.')]}


# def test_invalid_form_service_type(create_oerder_data):

#     create_oerder_data['service_type'] = 'AAA'

#     form = CreateQuotasForm(data=create_oerder_data)

#     assert not form.is_valid()

#     assert form.errors == {'service_type': ['Select a valid choice. AAA is not one of the available choices.']}


# def test_invalid_form_price(create_oerder_data):

#     create_oerder_data['price'] = '100.0.0'

#     form = CreateQuotasForm(data=create_oerder_data)

#     assert not form.is_valid()

#     assert form.errors == {'price': ['Enter a number.']}
