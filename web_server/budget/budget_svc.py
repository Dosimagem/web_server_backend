from web_server.budget.serializers import (
    ClinicDosimetryBudgetSerializer,
    CompModelBudgetSerilizer,
    PreClinicDosimetryBudgetSerializer,
    RadiosinoSerialier,
    SegmentantioQuantificationSerialier,
)
from web_server.service.models import Order


class BudgetChoice:
    def __init__(self, service_name):
        self.service_name = service_name

    serializer = {
        Order.ServicesName.COMPUTATIONAL_MODELLING.label: CompModelBudgetSerilizer,
        Order.ServicesName.PRECLINIC_DOSIMETRY.label: PreClinicDosimetryBudgetSerializer,
        Order.ServicesName.CLINIC_DOSIMETRY.label: ClinicDosimetryBudgetSerializer,
        Order.ServicesName.SEGMENTANTION_QUANTIFICATION.label: SegmentantioQuantificationSerialier,
        Order.ServicesName.RADIOSYNOVIORTHESIS.label: RadiosinoSerialier,
    }

    email_template = {
        Order.ServicesName.COMPUTATIONAL_MODELLING.label: 'budget/comp_model_budget.txt',
        Order.ServicesName.PRECLINIC_DOSIMETRY.label: 'budget/preclinic_dosi_budget.txt',
        Order.ServicesName.CLINIC_DOSIMETRY.label: 'budget/general_budget.txt',
        Order.ServicesName.SEGMENTANTION_QUANTIFICATION.label: 'budget/general_budget.txt',
        Order.ServicesName.RADIOSYNOVIORTHESIS.label: 'budget/general_budget.txt',
    }

    def get_serializer(self):
        return self.serializer[self.service_name]

    def get_email_template(self):
        return self.email_template[self.service_name]