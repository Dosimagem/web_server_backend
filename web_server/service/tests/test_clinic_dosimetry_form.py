from decimal import Decimal
import pytest

from django.utils.translation import gettext as _

from web_server.service.forms import ClinicDosimetryAnalysisCreateForm
from web_server.service.models import Order


def test_create_form(clinic_dosimetry_info, clinic_dosimetry_file):

    form = ClinicDosimetryAnalysisCreateForm(data=clinic_dosimetry_info, files=clinic_dosimetry_file)

    assert form.is_valid()


@pytest.mark.parametrize('field', [
    'user',
    'calibration',
    'order',
    'images'
])
def test_missing_fields(field, clinic_dosimetry_info, clinic_dosimetry_file):

    clinic_dosimetry_file.pop(field) if field == 'images' else clinic_dosimetry_info.pop(field)

    form = ClinicDosimetryAnalysisCreateForm(data=clinic_dosimetry_info, files=clinic_dosimetry_file)

    assert not form.is_valid()

    assert form.errors == {field: [_('This field is required.')]}


def test_invalid_order_of_wrong_service(user, preclinic_order, calibration, clinic_dosimetry_file):

    data = {
        'user': user,
        'calibration': calibration,
        'order': preclinic_order,
    }

    form = ClinicDosimetryAnalysisCreateForm(data=data, files=clinic_dosimetry_file)

    assert not form.is_valid()

    assert form.errors ==  {'__all__': ['Este serviço não foi contratado nesse pedido.']}
