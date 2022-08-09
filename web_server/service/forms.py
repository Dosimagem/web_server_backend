from django import forms

from web_server.service.models import DosimetryOrder


class DosimetryOrderForm(forms.ModelForm):

    class Meta:
        model = DosimetryOrder
        fields = 'camera_factor', 'radionuclide', 'injected_activity', 'injection_datetime', 'images'

    def save(self, requester, service, amount):
        super().save(commit=False)
        order = DosimetryOrder(requester=requester,
                               service=service,
                               amount=amount,
                               camera_factor=self.cleaned_data['camera_factor'],
                               radionuclide=self.cleaned_data['radionuclide'],
                               injected_activity=self.cleaned_data['injected_activity'],
                               injection_datetime=self.cleaned_data['injection_datetime'],
                               images=self.cleaned_data['images'],
                               )
        return order.save()
