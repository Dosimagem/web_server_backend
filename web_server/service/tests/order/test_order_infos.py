import pytest
from django.core.files.base import ContentFile

from web_server.conftest import DATETIME_TIMEZONE
from web_server.service.models import (
    ClinicDosimetryAnalysis,
    Order,
    PreClinicDosimetryAnalysis,
    SegmentationAnalysis,
)
from web_server.service.order_svc import OrderInfos


@pytest.mark.parametrize(
    'model, service_name',
    [
        (ClinicDosimetryAnalysis, Order.CLINIC_DOSIMETRY),
        (PreClinicDosimetryAnalysis, Order.PRECLINIC_DOSIMETRY),
        (SegmentationAnalysis, Order.SEGMENTANTION_QUANTIFICATION),
    ],
)
def test_order_analisys_counts(model, service_name, user, first_calibration):

    order = Order.objects.create(
        user=user,
        quantity_of_analyzes=12,
        remaining_of_analyzes=0,
        price='1000.00',
        service_name=service_name,
        status_payment=Order.CONFIRMED,
    )

    if service_name in [Order.CLINIC_DOSIMETRY, Order.PRECLINIC_DOSIMETRY]:
        data = {
            'calibration': first_calibration,
            'order': order,
            'images': ContentFile(b'CT e SPET files 1', name='images.zip'),
            'injected_activity': 50,
            'administration_datetime': DATETIME_TIMEZONE,
        }
    elif service_name == Order.SEGMENTANTION_QUANTIFICATION:
        data = {
            'order': order,
            'images': ContentFile(b'CT e SPET files 1', name='images.zip'),
        }

    # Analisando informações
    model.objects.create(**data, analysis_name='Analysis 1', status=model.ANALYZING_INFOS)
    model.objects.create(**data, analysis_name='Analysis 2', status=model.ANALYZING_INFOS)

    # Processando
    model.objects.create(**data, analysis_name='Analysis 3', status=model.PROCESSING)
    model.objects.create(**data, analysis_name='Analysis 4', status=model.PROCESSING)
    model.objects.create(**data, analysis_name='Analysis 5', status=model.PROCESSING)

    # Dados enviados
    model.objects.create(**data, analysis_name='Analysis 6')
    model.objects.create(**data, analysis_name='Analysis 7')

    # Dados invalidos
    model.objects.create(**data, analysis_name='Analysis 8', status=model.INVALID_INFOS)
    model.objects.create(**data, analysis_name='Analysis 9', status=model.INVALID_INFOS)
    model.objects.create(**data, analysis_name='Analysis 10', status=model.INVALID_INFOS)
    model.objects.create(**data, analysis_name='Analysis 11', status=model.INVALID_INFOS)

    # Concluído
    model.objects.create(**data, analysis_name='Analysis 12', status=model.CONCLUDED)

    order_infos = OrderInfos(order)

    assert order_infos.analysis_status_count() == {
        'data_set': 2,
        'invalid_infos': 4,
        'concluded': 1,
        'processing': 3,
        'analyzing_infos': 2,
    }


def test_order_payment(clinic_order):

    clinic_order.status_payment = Order.PRECLINIC_DOSIMETRY

    order_infos = OrderInfos(clinic_order)

    assert not order_infos.has_payment_confirmed()

    clinic_order.status_payment = Order.CONFIRMED

    assert order_infos.has_payment_confirmed()


def test_order_analisys_available(clinic_order):

    clinic_order.remaining_of_analyzes = 0

    order_infos = OrderInfos(clinic_order)

    assert not order_infos.are_analyzes_available()

    clinic_order.remaining_of_analyzes = 1

    assert order_infos.are_analyzes_available()
