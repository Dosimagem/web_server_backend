from django import forms


class ClinicDosimetryAnalysisCreateFormApi(forms.Form):
    calibration_id = forms.UUIDField()
