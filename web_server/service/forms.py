from django import forms

from web_server.service.models import UserQuota


class DisableSaveFormException(Exception):
    def __init__(self, message='Save diabled for this form.'):
        self.message = message
        super().__init__(self.message)


class CreateQuotasForm(forms.ModelForm):

    class Meta:
        model = UserQuota
        fields = ('amount', 'price', 'service_type', )

    def save(self):
        raise DisableSaveFormException()


class UpdateQuotasForm(forms.ModelForm):

    class Meta:
        model = UserQuota
        fields = ('amount', )

    def save(self):
        raise DisableSaveFormException()
