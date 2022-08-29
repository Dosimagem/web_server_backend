from django import forms

# from web_server.service.models import UserQuotas


class QuotasForm(forms.Form):

    clinic_dosimetry = forms.IntegerField(min_value=0, required=False)

    # class Meta:
    #     model = UserQuotas
    #     fields = ('clinic_dosimetry',)
