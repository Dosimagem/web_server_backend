import pytest

from web_server.service.forms import ClinicDosimetryAnalysisCreateForm


def test_create_form(clinic_dosimetry_info, clinic_dosimetry_file):

    form = ClinicDosimetryAnalysisCreateForm(data=clinic_dosimetry_info, files=clinic_dosimetry_file)

    assert form.is_valid()


@pytest.mark.parametrize(
    'field',
    [
        'calibration',
        'order',
        'images',
        'analysis_name',
        'injected_activity',
        'administration_datetime',
    ],
)
def test_missing_fields(field, clinic_dosimetry_info, clinic_dosimetry_file):

    clinic_dosimetry_file.pop(field) if field == 'images' else clinic_dosimetry_info.pop(field)

    form = ClinicDosimetryAnalysisCreateForm(data=clinic_dosimetry_info, files=clinic_dosimetry_file)

    assert not form.is_valid()

    assert form.errors == {field: ['Este campo é obrigatório.']}


def test_invalid_order_of_wrong_service(preclinic_order, clinic_dosimetry_info, clinic_dosimetry_file):

    clinic_dosimetry_info['order'] = preclinic_order

    form = ClinicDosimetryAnalysisCreateForm(data=clinic_dosimetry_info, files=clinic_dosimetry_file)

    assert not form.is_valid()

    assert form.errors == {'__all__': ['Este serviço não foi contratado nesse pedido.']}


def test_invalid_create_form_field_must_be_positive(clinic_dosimetry_info, calibration_file):

    clinic_dosimetry_info['injected_activity'] = -clinic_dosimetry_info['injected_activity']

    form = ClinicDosimetryAnalysisCreateForm(data=clinic_dosimetry_info, files=calibration_file)

    assert not form.is_valid()

    msg = 'Certifique-se que este valor seja maior ou igual a 0.0.'

    assert form.errors == {'injected_activity': [msg]}


def test_invalid_create_form_analysis_name_must_be_unique_per_order(
    clinic_dosimetry, clinic_dosimetry_info, clinic_dosimetry_file
):

    form = ClinicDosimetryAnalysisCreateForm(data=clinic_dosimetry_info, files=clinic_dosimetry_file)

    assert not form.is_valid()

    assert form.errors == {'__all__': ['Dosimetria clínica com este Order e Nome da análise já existe.']}


def test_invalid_analysis_name_length_must_least_3(clinic_dosimetry_info, clinic_dosimetry_file):

    clinic_dosimetry_info['analysis_name'] = '22'

    form = ClinicDosimetryAnalysisCreateForm(data=clinic_dosimetry_info, files=clinic_dosimetry_file)

    assert not form.is_valid()

    expected = ['Certifique-se de que o valor tenha no mínimo 3 caracteres (ele possui 2).']

    assert form.errors == {'analysis_name': expected}
