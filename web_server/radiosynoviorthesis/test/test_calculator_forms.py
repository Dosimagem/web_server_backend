import pytest


from web_server.radiosynoviorthesis.forms import CalculatorForm


def test_forms_successfull(calculator_input):

    form = CalculatorForm(calculator_input)

    assert form.is_valid()

    assert form.cleaned_data['thickness'] == '1 mm'


@pytest.mark.parametrize('field, value, error', [
    ('radionuclide', 'AA-666',
        {
            'radionuclide': ['Faça uma escolha válida. AA-666 não é uma das escolhas disponíveis.']
        }
     ),
    ('thickness', '4 cm',
        {
            'thickness': ['Faça uma escolha válida. 4 cm não é uma das escolhas disponíveis.']
        }
     ),
    ('surface', -10,
        {
            'surface': ['Certifique-se que este valor seja maior ou igual a 0.0.']
        }
     ),
    ('surface', 'd-10',
        {
            'surface': ['Informe um número.']
        }
     ),
])
def test_fail_forms_invalid_values(field, value, error, calculator_input):

    calculator_input[field] = value

    form = CalculatorForm(calculator_input)

    assert not form.is_valid()

    assert error == form.errors


@pytest.mark.parametrize('field, error', [
    ('radionuclide', {'radionuclide': ['Este campo é obrigatório.']}),
    ('thickness', {'thickness': ['Este campo é obrigatório.']}),
    ('surface', {'surface': ['Este campo é obrigatório.']}),
])
def test_fail_forms_missing_fields(field, error, calculator_input):

    calculator_input.pop(field)

    form = CalculatorForm(calculator_input)

    assert not form.is_valid()

    assert error == form.errors
