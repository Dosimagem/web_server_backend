from web_server.service.forms import (
    ClinicDosimetryAnalysisCreateForm,
    ClinicDosimetryAnalysisUpdateForm,
    PreClinicDosimetryAnalysisCreateForm,
    PreClinicDosimetryAnalysisUpdateForm,
    RadiosynoAnalysisCreateForm,
    RadiosynoAnalysisUpdateForm,
    SegmentationAnalysisCreateForm,
    SegmentationAnalysisUpdateForm,
)
from web_server.service.models import (
    ClinicDosimetryAnalysis,
    Order,
    PreClinicDosimetryAnalysis,
    RadiosynoAnalysis,
    SegmentationAnalysis,
)


class AnalisysChoice:

    _update_forms = {
        Order.ServicesName.PRECLINIC_DOSIMETRY.value: PreClinicDosimetryAnalysisUpdateForm,
        Order.ServicesName.CLINIC_DOSIMETRY.value: ClinicDosimetryAnalysisUpdateForm,
        Order.ServicesName.SEGMENTANTION_QUANTIFICATION.value: SegmentationAnalysisUpdateForm,
        Order.ServicesName.RADIOSYNOVIORTHESIS.value: RadiosynoAnalysisUpdateForm,
    }

    _create_forms = {
        Order.ServicesName.PRECLINIC_DOSIMETRY.value: PreClinicDosimetryAnalysisCreateForm,
        Order.ServicesName.CLINIC_DOSIMETRY.value: ClinicDosimetryAnalysisCreateForm,
        Order.ServicesName.SEGMENTANTION_QUANTIFICATION.value: SegmentationAnalysisCreateForm,
        Order.ServicesName.RADIOSYNOVIORTHESIS.value: RadiosynoAnalysisCreateForm,
    }

    _models = {
        Order.ServicesName.PRECLINIC_DOSIMETRY.value: PreClinicDosimetryAnalysis,
        Order.ServicesName.CLINIC_DOSIMETRY.value: ClinicDosimetryAnalysis,
        Order.ServicesName.SEGMENTANTION_QUANTIFICATION.value: SegmentationAnalysis,
        Order.ServicesName.RADIOSYNOVIORTHESIS.value: RadiosynoAnalysis,
    }

    def __init__(self, order):
        self.order = order

    @property
    def update_form(self):
        return self._update_forms[self.order.service_name]

    @property
    def create_form(self):
        return self._create_forms[self.order.service_name]

    @property
    def model(self):
        return self._models[self.order.service_name]
