import pytest
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.utils.translation import gettext as _

from web_server.service.forms import CreateCalibrationForm
from web_server.service.models import Calibration

User = get_user_model()


def test_valid_create_form_calibration(calibration_infos, calibration_file):

    form = CreateCalibrationForm(data=calibration_infos, files=calibration_file)

    assert form.is_valid()

    for f in form.fields:
        if isinstance(form.cleaned_data[f], ContentFile):
            form.cleaned_data[f] == calibration_file[f]
        else:
            assert form.cleaned_data[f] == calibration_infos[f]


@pytest.mark.parametrize(
    'field',
    ('syringe_activity', 'residual_syringe_activity', 'phantom_volume'),
)
def test_invalid_create_form_field_must_be_positive(field, calibration_infos, calibration_file):

    calibration_infos[field] = -calibration_infos[field]

    form = CreateCalibrationForm(data=calibration_infos, files=calibration_file)

    assert not form.is_valid()

    msg = _('Ensure this value is greater than or equal to %(limit_value)s.')

    msg = msg % {'limit_value': 0.0}

    assert form.errors == {field: [msg]}


@pytest.mark.parametrize(
    'field',
    [
        'user',
        'isotope',
        'calibration_name',
        'syringe_activity',
        'residual_syringe_activity',
        'measurement_datetime',
        'phantom_volume',
        'acquisition_time',
        'images',
    ],
)
def test_invalid_missing_fields(field, calibration_infos, calibration_file):

    calibration_file.pop(field) if field == 'images' else calibration_infos.pop(field)

    form = CreateCalibrationForm(data=calibration_infos, files=calibration_file)

    assert not form.is_valid()

    assert form.errors == {field: [_('This field is required.')]}


def test_invalid_isotope(calibration_infos, calibration_file):

    calibration_infos['isotope'] = 'wrong'

    form = CreateCalibrationForm(data=calibration_infos, files=calibration_file)

    assert not form.is_valid()

    assert form.errors == {'isotope': [_('Select a valid choice. That choice is not one of the available choices.')]}


def test_valid_create_form_field_save(calibration_infos, calibration_file):

    form = CreateCalibrationForm(data=calibration_infos, files=calibration_file)

    assert form.is_valid()

    assert form.save()

    assert Calibration.objects.exists()


def test_invalid_calibration_name_length_must_least_3(calibration_infos, calibration_file):

    calibration_infos['calibration_name'] = '22'

    form = CreateCalibrationForm(data=calibration_infos, files=calibration_file)

    assert not form.is_valid()

    expected = ['Certifique-se de que o valor tenha no mínimo 3 caracteres (ele possui 2).']

    assert form.errors == {'calibration_name': expected}
