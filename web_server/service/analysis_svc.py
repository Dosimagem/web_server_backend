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
        Order.PRECLINIC_DOSIMETRY: PreClinicDosimetryAnalysisUpdateForm,
        Order.CLINIC_DOSIMETRY: ClinicDosimetryAnalysisUpdateForm,
        Order.SEGMENTANTION_QUANTIFICATION: SegmentationAnalysisUpdateForm,
        Order.RADIOSYNOVIORTHESIS: RadiosynoAnalysisUpdateForm,
    }

    _create_forms = {
        Order.PRECLINIC_DOSIMETRY: PreClinicDosimetryAnalysisCreateForm,
        Order.CLINIC_DOSIMETRY: ClinicDosimetryAnalysisCreateForm,
        Order.SEGMENTANTION_QUANTIFICATION: SegmentationAnalysisCreateForm,
        Order.RADIOSYNOVIORTHESIS: RadiosynoAnalysisCreateForm,
    }

    _models = {
        Order.PRECLINIC_DOSIMETRY: PreClinicDosimetryAnalysis,
        Order.CLINIC_DOSIMETRY: ClinicDosimetryAnalysis,
        Order.SEGMENTANTION_QUANTIFICATION: SegmentationAnalysis,
        Order.RADIOSYNOVIORTHESIS: RadiosynoAnalysis,
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
