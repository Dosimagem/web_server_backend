import pytest

from web_server.budget.budget_svc import BudgetChoice
from web_server.budget.serializers import (
    ClinicDosimetryBudgetSerializer,
    CompModelBudgetSerilizer,
    PreClinicDosimetryBudgetSerializer,
    RadiosinoSerialier,
    SegmentantioQuantificationSerialier,
)
from web_server.service.models import Order


@pytest.mark.parametrize(
    'serializerClass, service_name',
    [
        (ClinicDosimetryBudgetSerializer, Order.ServicesName.CLINIC_DOSIMETRY.label),
        (PreClinicDosimetryBudgetSerializer, Order.ServicesName.PRECLINIC_DOSIMETRY.label),
        (SegmentantioQuantificationSerialier, Order.ServicesName.SEGMENTANTION_QUANTIFICATION.label),
        (RadiosinoSerialier, Order.ServicesName.RADIOSYNOVIORTHESIS.label),
        (CompModelBudgetSerilizer, Order.ServicesName.COMPUTATIONAL_MODELLING.label),
    ],
)
def test_get_serializer(serializerClass, service_name):

    sc = BudgetChoice(service_name=service_name).get_serializer()

    serializer = sc()

    assert isinstance(serializer, serializerClass)


@pytest.mark.parametrize(
    'email_template_txt, email_template_html, service_name',
    [
        (
            'budget/general_budget.txt',
            'budget/general_budget.html',
            Order.ServicesName.CLINIC_DOSIMETRY.label,
        ),
        (
            'budget/preclinic_dosi_budget.txt',
            'budget/preclinic_dosi_budget.html',
            Order.ServicesName.PRECLINIC_DOSIMETRY.label,
        ),
        (
            'budget/general_budget.txt',
            'budget/general_budget.html',
            Order.ServicesName.SEGMENTANTION_QUANTIFICATION.label,
        ),
        (
            'budget/general_budget.txt',
            'budget/general_budget.html',
            Order.ServicesName.RADIOSYNOVIORTHESIS.label,
        ),
        (
            'budget/comp_model_budget.txt',
            'budget/comp_model_budget.html',
            Order.ServicesName.COMPUTATIONAL_MODELLING.label,
        ),
    ],
)
def test_get_email_template(email_template_txt, email_template_html, service_name):

    et, et_html = BudgetChoice(service_name=service_name).get_email_template()

    assert et == email_template_txt
    assert et_html == email_template_html
