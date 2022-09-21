import pytest

from django.utils.translation import gettext as _

from web_server.service.forms import PreClinicDosimetryAnalysisCreateForm


def test_create_form(preclinic_dosimetry_info, preclinic_dosimetry_file):

    form = PreClinicDosimetryAnalysisCreateForm(data=preclinic_dosimetry_info, files=preclinic_dosimetry_file)

    assert form.is_valid()


@pytest.mark.parametrize('field', [
    'user',
    'calibration',
    'order',
    'images',
    'analysis_name',
    'injected_activity',
    'administration_datetime',
])
def test_missing_fields(field, preclinic_dosimetry_info, preclinic_dosimetry_file):

    preclinic_dosimetry_file.pop(field) if field == 'images' else preclinic_dosimetry_info.pop(field)

    form = PreClinicDosimetryAnalysisCreateForm(data=preclinic_dosimetry_info, files=preclinic_dosimetry_file)

    assert not form.is_valid()

    assert form.errors == {field: [_('This field is required.')]}


def test_invalid_order_of_wrong_service(order, preclinic_dosimetry_info, preclinic_dosimetry_file):

    preclinic_dosimetry_info['order'] = order

    form = PreClinicDosimetryAnalysisCreateForm(data=preclinic_dosimetry_info, files=preclinic_dosimetry_file)

    assert not form.is_valid()

    assert form.errors == {'__all__': ['Este serviço não foi contratado nesse pedido.']}


def test_invalid_create_form_field_must_be_positive(preclinic_dosimetry_info, preclinic_dosimetry_file):

    preclinic_dosimetry_info['injected_activity'] = -preclinic_dosimetry_info['injected_activity']

    form = PreClinicDosimetryAnalysisCreateForm(data=preclinic_dosimetry_info, files=preclinic_dosimetry_file)

    assert not form.is_valid()

    msg = _('Ensure this value is greater than or equal to %(limit_value)s.')

    msg = msg % {'limit_value': 0.0}

    assert form.errors == {'injected_activity': [msg]}


def test_invalid_create_form_analysis_name_must_be_unique_per_order(preclinic_dosimetry,
                                                                   preclinic_dosimetry_info,
                                                                   preclinic_dosimetry_file):

    form = PreClinicDosimetryAnalysisCreateForm(data=preclinic_dosimetry_info, files=preclinic_dosimetry_file)

    assert not form.is_valid()

    assert form.errors == {'__all__': ['Preclinic Dosimetry com este Order e Analysis Name já existe.']}
