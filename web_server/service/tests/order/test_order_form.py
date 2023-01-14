from decimal import Decimal

from web_server.service.forms import CreateOrderForm
from web_server.service.models import Order


def test_valid_form(create_order_data):

    form = CreateOrderForm(data=create_order_data)

    assert form.is_valid()
    assert form.cleaned_data['quantity_of_analyzes'] == 10
    assert form.cleaned_data['remaining_of_analyzes'] == 10
    assert form.cleaned_data['price'] == Decimal('1000.00')
    assert form.cleaned_data['service_name'] == Order.ServicesName.CLINIC_DOSIMETRY.value


def test_invalid_form_negative_quantity_of_analyzes(create_order_data):

    create_order_data['quantity_of_analyzes'] = -10

    form = CreateOrderForm(data=create_order_data)

    assert not form.is_valid()

    msg = 'Certifique-se que este valor seja maior ou igual a 0.'

    assert form.errors == {'quantity_of_analyzes': [msg]}


def test_invalid_form_quantity_of_analyzes(create_order_data):

    create_order_data['quantity_of_analyzes'] = '1..0'

    form = CreateOrderForm(data=create_order_data)

    assert not form.is_valid()

    assert form.errors == {'quantity_of_analyzes': ['Informe um número inteiro.']}


def test_invalid_form_remaining_of_analyzes_must_be_lower_that_quantity_of_analyzes(
    create_order_data,
):

    create_order_data['quantity_of_analyzes'] = '1'
    create_order_data['remaining_of_analyzes'] = '2'

    form = CreateOrderForm(data=create_order_data)

    assert not form.is_valid()

    assert form.errors == {
        'remaining_of_analyzes': ['A análise restante deve ser menor que o número do campo de análise.']
    }


def test_invalid_form_price(create_order_data):

    create_order_data['price'] = '100.0.0'

    form = CreateOrderForm(data=create_order_data)

    assert not form.is_valid()

    assert form.errors == {'price': ['Informe um número.']}


def test_invalid_form_service_type(create_order_data):

    create_order_data['service_name'] = 'AAA'

    form = CreateOrderForm(data=create_order_data)

    assert not form.is_valid()

    expected = ['Faça uma escolha válida. AAA não é uma das escolhas disponíveis.']

    assert form.errors == {'service_name': expected}
