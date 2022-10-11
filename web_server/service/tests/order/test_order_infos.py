import pytest
from django.core.files.base import ContentFile
from web_server.conftest import DATETIME_TIMEZONE

from web_server.service.models import ClinicDosimetryAnalysis, Order, PreClinicDosimetryAnalysis
from web_server.service.order_svc import OrderInfos


@pytest.mark.parametrize('model, service_name', [
    (ClinicDosimetryAnalysis, Order.CLINIC_DOSIMETRY),
    (PreClinicDosimetryAnalysis, Order.PRECLINIC_DOSIMETRY)
])
def test_order_analisys_infos(model, service_name, user, first_calibration):

    order = Order.objects.create(user=user,
                                 quantity_of_analyzes=10,
                                 remaining_of_analyzes=4,
                                 price='1000.00',
                                 service_name=service_name,
                                 status_payment=Order.CONFIRMED
                                 )

    data = {
        'calibration': first_calibration,
        'order': order,
        'images': ContentFile(b'CT e SPET files 1', name='images.zip'),
        'injected_activity': 50,
        'administration_datetime': DATETIME_TIMEZONE

    }

    # Analisando informações
    model.objects.create(**data, analysis_name='Analysis 1', status=model.ANALYZING_INFOS)
    model.objects.create(**data, analysis_name='Analysis 2', status=model.ANALYZING_INFOS)

    # Processando
    model.objects.create(**data, analysis_name='Analysis 3', status=model.PROCESSING)
    model.objects.create(**data, analysis_name='Analysis 4', status=model.PROCESSING)
    model.objects.create(**data, analysis_name='Analysis 5', status=model.PROCESSING)

    # Concluído
    model.objects.create(**data, analysis_name='Analysis 6', status=model.CONCLUDED)

    order_infos = OrderInfos(order)

    assert order_infos.analysis_status_count() == {'concluded': 1, 'processing': 3, 'analyzing_infos': 2}
