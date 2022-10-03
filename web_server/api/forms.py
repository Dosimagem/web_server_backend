from django import forms


class PreClinicAndClinicDosimetryAnalysisCreateFormApi(forms.Form):
    calibration_id = forms.UUIDField()


class PreClinicAndClinicDosimetryAnalysisUpdateFormApi(PreClinicAndClinicDosimetryAnalysisCreateFormApi):
    ...
