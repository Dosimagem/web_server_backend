from web_server.service.analysis_svc import AnalisysChoice
from web_server.service.forms import (
    ClinicDosimetryAnalysisCreateForm,
    ClinicDosimetryAnalysisUpdateForm,
    PreClinicDosimetryAnalysisCreateForm,
    PreClinicDosimetryAnalysisUpdateForm,
)
from web_server.service.models import ClinicDosimetryAnalysis, PreClinicDosimetryAnalysis


def test_get_forms_update(clinic_order, preclinic_order):

    analysis_svc = AnalisysChoice(order=clinic_order)

    assert ClinicDosimetryAnalysisUpdateForm == analysis_svc.update_form

    analysis_svc = AnalisysChoice(order=preclinic_order)

    assert PreClinicDosimetryAnalysisUpdateForm == analysis_svc.update_form


def test_get_forms_create(clinic_order, preclinic_order):

    analysis_svc = AnalisysChoice(order=clinic_order)

    assert ClinicDosimetryAnalysisCreateForm == analysis_svc.create_form

    analysis_svc = AnalisysChoice(order=preclinic_order)

    assert PreClinicDosimetryAnalysisCreateForm == analysis_svc.create_form


def test_get_model(clinic_order, preclinic_order):

    analysis_svc = AnalisysChoice(order=clinic_order)

    assert ClinicDosimetryAnalysis == analysis_svc.model

    analysis_svc = AnalisysChoice(order=preclinic_order)

    assert PreClinicDosimetryAnalysis == analysis_svc.model
