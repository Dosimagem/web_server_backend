import pytest

from web_server.service.forms import PreClinicDosimetryAnalysisCreateForm


def test_create_form(preclinic_dosimetry_info, preclinic_dosimetry_file):

    form = PreClinicDosimetryAnalysisCreateForm(data=preclinic_dosimetry_info, files=preclinic_dosimetry_file)

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
def test_missing_fields(field, preclinic_dosimetry_info, preclinic_dosimetry_file):

    preclinic_dosimetry_file.pop(field) if field == 'images' else preclinic_dosimetry_info.pop(field)

    form = PreClinicDosimetryAnalysisCreateForm(data=preclinic_dosimetry_info, files=preclinic_dosimetry_file)

    assert not form.is_valid()

    assert form.errors == {field: ['This field is required.']}


def test_invalid_order_of_wrong_service(clinic_order, preclinic_dosimetry_info, preclinic_dosimetry_file):

    preclinic_dosimetry_info['order'] = clinic_order

    form = PreClinicDosimetryAnalysisCreateForm(data=preclinic_dosimetry_info, files=preclinic_dosimetry_file)

    assert not form.is_valid()

    assert form.errors == {'__all__': ['Este serviço não foi contratado nesse pedido.']}


def test_invalid_create_form_field_must_be_positive(preclinic_dosimetry_info, preclinic_dosimetry_file):

    preclinic_dosimetry_info['injected_activity'] = -preclinic_dosimetry_info['injected_activity']

    form = PreClinicDosimetryAnalysisCreateForm(data=preclinic_dosimetry_info, files=preclinic_dosimetry_file)

    assert not form.is_valid()

    msg = 'Ensure this value is greater than or equal to 0.0.'

    assert form.errors == {'injected_activity': [msg]}


def test_invalid_create_form_analysis_name_must_be_unique_per_order(
    preclinic_dosimetry, preclinic_dosimetry_info, preclinic_dosimetry_file
):

    form = PreClinicDosimetryAnalysisCreateForm(data=preclinic_dosimetry_info, files=preclinic_dosimetry_file)

    assert not form.is_valid()

    assert form.errors == {'__all__': ['Preclinic Dosimetry com este Order e Analysis Name já existe.']}


def test_invalid_analysis_name_length_must_least_3(preclinic_dosimetry_info, preclinic_dosimetry_file):

    preclinic_dosimetry_info['analysis_name'] = '2'

    form = PreClinicDosimetryAnalysisCreateForm(data=preclinic_dosimetry_info, files=preclinic_dosimetry_file)

    assert not form.is_valid()

    expected = ['Certifique-se de que o valor tenha no mínimo 3 caracteres (ele possui 1).']

    assert form.errors == {'analysis_name': expected}
