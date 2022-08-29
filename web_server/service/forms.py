from django import forms

# from web_server.service.models import UserQuotas


class QuotasForm(forms.Form):

    clinic_dosimetry = forms.IntegerField(min_value=0, required=False)

    # class Meta:
    #     model = UserQuotas
    #     fields = ('clinic_dosimetry',)

    def clean(self):

        at_least_one_this_fields = ['clinic_dosimetry']
        at_least = False

        for field in at_least_one_this_fields:
            if field in self.data:
                at_least = True

        if not at_least:
            list_fields = ', '.join(at_least_one_this_fields)
            raise forms.ValidationError(f'Must be at least once in these fields: [{list_fields}]')
