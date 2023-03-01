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
        'Modelagem Computacional': CompModelBudgetSerilizer,  # TODO: Colocar isso no choice models depois
        Order.ServicesName.PRECLINIC_DOSIMETRY.label: PreClinicDosimetryBudgetSerializer,
        Order.ServicesName.CLINIC_DOSIMETRY.label: ClinicDosimetryBudgetSerializer,
        Order.ServicesName.SEGMENTANTION_QUANTIFICATION.label: SegmentantioQuantificationSerialier,
        Order.ServicesName.RADIOSYNOVIORTHESIS.label: RadiosinoSerialier,
    }

    email_template = {
        'Modelagem Computacional': 'budget/comp_model_budget',  # TODO: Colocar isso no choice models depois
        Order.ServicesName.PRECLINIC_DOSIMETRY.label: 'budget/preclinic_dosi_budget',
        Order.ServicesName.CLINIC_DOSIMETRY.label: 'budget/general_budget',
        Order.ServicesName.SEGMENTANTION_QUANTIFICATION.label: 'budget/general_budget',
        Order.ServicesName.RADIOSYNOVIORTHESIS.label: 'budget/general_budget',
    }

    def get_serializer(self):
        return self.serializer[self.service_name]

    def get_email_template(self):
        name = self.email_template[self.service_name]
        return name + '.txt', name + '.html'
