from decimal import Decimal
import pytest

from django.utils.translation import gettext as _

from web_server.service.forms import PreClinicDosimetryAnalysisCreateForm
from web_server.service.models import Order


def test_create_form(preclinic_dosimetry_info, preclinic_dosimetry_file):

    form = PreClinicDosimetryAnalysisCreateForm(data=preclinic_dosimetry_info, files=preclinic_dosimetry_file)

    assert form.is_valid()


@pytest.mark.parametrize('field', [
    'user',
    'calibration',
    'order',
    'images'
])
def test_missing_fields(field, preclinic_dosimetry_info, preclinic_dosimetry_file):

    preclinic_dosimetry_file.pop(field) if field == 'images' else preclinic_dosimetry_info.pop(field)

    form = PreClinicDosimetryAnalysisCreateForm(data=preclinic_dosimetry_info, files=preclinic_dosimetry_file)

    assert not form.is_valid()

    assert form.errors == {field: [_('This field is required.')]}


def test_invalid_order_of_wrong_service(user, order, calibration, preclinic_dosimetry_file):

    data = {
        'user': user,
        'calibration': calibration,
        'order': order,
    }

    form = PreClinicDosimetryAnalysisCreateForm(data=data, files=preclinic_dosimetry_file)

    assert not form.is_valid()

    assert form.errors ==  {'__all__': ['Este serviço não foi contratado nesse pedido.']}