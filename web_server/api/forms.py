from django import forms
from django.contrib.auth import get_user_model


User = get_user_model()


class PreClinicAndClinicDosimetryAnalysisCreateFormApi(forms.Form):
    calibration_id = forms.UUIDField()


class PreClinicAndClinicDosimetryAnalysisUpdateFormApi(PreClinicAndClinicDosimetryAnalysisCreateFormApi):
    ...


# TODO: Testar de forma unitaria o form.
class UpdateEmailForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('email',)
