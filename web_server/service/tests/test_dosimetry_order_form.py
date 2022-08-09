from unittest import mock
import pytest

from django.core.files.uploadedfile import SimpleUploadedFile

from web_server.conftest import DATETIME_TIMEZONE
from web_server.service.forms import DosimetryOrderForm
from web_server.service.models import DosimetryOrder


@pytest.fixture
def payload():
    return {
        'camera_factor': 50,
        'radionuclide': 'Lu-171',
        'injected_activity': 50.0,
        'injection_datetime': DATETIME_TIMEZONE,
    }


@pytest.fixture
def payload_file():
    return {'images': SimpleUploadedFile('images.zip', b'Images bytes')}


def test_dosimetry_form(payload, payload_file):

    form = DosimetryOrderForm(payload, payload_file)

    assert form.is_valid()


@pytest.mark.parametrize(
    'field',
    ['camera_factor', 'radionuclide', 'injected_activity', 'injection_datetime'],
)
def test_dosimetry_form_field_required(payload, payload_file, field):

    del payload[field]
    form = DosimetryOrderForm(payload, payload_file)

    assert not form.is_valid()

    expected = ['This field is required.']
    assert expected == form.errors[field]


def test_dosimetry_form_file(payload):

    form = DosimetryOrderForm(payload)

    assert not form.is_valid()

    expected = ['This field is required.']
    assert expected == form.errors['images']


def test_camera_factor_must_be_float(payload):
    payload['camera_factor'] = str(30)

    form = DosimetryOrderForm(payload)

    form.full_clean()

    assert isinstance(form.cleaned_data['camera_factor'], float)


def test_injected_activity_must_be_float(payload):
    payload['injected_activity'] = str(30)

    form = DosimetryOrderForm(payload)

    form.full_clean()

    assert isinstance(form.cleaned_data['injected_activity'], float)


@pytest.mark.skip
@mock.patch('web_server.service.models.now')
def test_save(mock, payload, payload_file, dosimetry_clinical_service, user, datetime_now):

    form = DosimetryOrderForm(payload, payload_file)

    form.save(requester=user, service=dosimetry_clinical_service, amount=1)

    assert DosimetryOrder.objects.exists()

    order = DosimetryOrder.objects.first()

    assert order.requester.id == user.id
    assert order.service == dosimetry_clinical_service
    assert order.amount == 1
    assert order.status == DosimetryOrder.AWAITING_PAYMENT
    assert order.camera_factor == payload['camera_factor']
    assert order.radionuclide == payload['radionuclide']
    assert order.injected_activity == payload['injected_activity']
    assert order.injection_datetime == payload['injection_datetime']

    t, date, time = datetime_now
    mock.return_value = t

    file_name = payload_file['images'].name

    assert order.images == f'{user}/images/{date}/{file_name}_{time}.zip'
