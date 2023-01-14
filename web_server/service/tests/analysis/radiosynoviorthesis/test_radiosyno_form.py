import pytest

from web_server.service.forms import RadiosynoAnalysisCreateForm


def test_create_form(radiosyno_analysis_info, radiosyno_analysis_file):

    form = RadiosynoAnalysisCreateForm(data=radiosyno_analysis_info, files=radiosyno_analysis_file)

    assert form.is_valid()


@pytest.mark.parametrize(
    'field',
    [
        'order',
        'images',
        'analysis_name',
        'isotope',
    ],
)
def test_missing_fields(field, radiosyno_analysis_info, radiosyno_analysis_file):

    radiosyno_analysis_file.pop(field) if field == 'images' else radiosyno_analysis_info.pop(field)

    form = RadiosynoAnalysisCreateForm(data=radiosyno_analysis_info, files=radiosyno_analysis_file)

    assert not form.is_valid()

    assert form.errors == {field: ['Este campo é obrigatório.']}


def test_invalid_order_of_wrong_service(preclinic_order, radiosyno_analysis_info, radiosyno_analysis_file):

    radiosyno_analysis_info['order'] = preclinic_order

    form = RadiosynoAnalysisCreateForm(data=radiosyno_analysis_info, files=radiosyno_analysis_file)

    assert not form.is_valid()

    assert form.errors == {'__all__': ['Este serviço não foi contratado nesse pedido.']}


def test_invalid_create_form_analysis_name_must_be_unique_per_order(
    radiosyno_analysis, radiosyno_analysis_info, radiosyno_analysis_file
):

    form = RadiosynoAnalysisCreateForm(data=radiosyno_analysis_info, files=radiosyno_analysis_file)

    assert not form.is_valid()

    assert form.errors == {'__all__': ['Radiosynoviorthesis Analysis com este Order e Analysis Name já existe.']}


def test_invalid_analysis_name_length_must_least_3(radiosyno_analysis_info, radiosyno_analysis_file):

    radiosyno_analysis_info['analysis_name'] = '22'

    form = RadiosynoAnalysisCreateForm(data=radiosyno_analysis_info, files=radiosyno_analysis_file)

    assert not form.is_valid()

    expected = ['Certifique-se de que o valor tenha no mínimo 3 caracteres (ele possui 2).']

    assert form.errors == {'analysis_name': expected}
