from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import ValidationError
from django.utils.translation import gettext as _

from web_server.core.models import CustomUser, UserProfile


class SignupForm(UserCreationForm):

    confirmed_email = forms.EmailField(label='confirmed_email')
    name = forms.CharField(label='name', max_length=150)
    phone = forms.CharField(label='phone', max_length=30)
    clinic = forms.CharField(label='clinic', max_length=30)
    role = forms.CharField(label='role', max_length=30)
    cpf = forms.CharField(max_length=11)
    cnpj = forms.CharField(max_length=14)

    class Meta:
        model = CustomUser
        fields = ('email', 'password1', 'password2',)

    def clean_name(self):
        return self.cleaned_data['name'].title()

    def clean_role(self):
        return self.cleaned_data['role'].lower()

    def clean_phone(self):
        return ''.join(d for d in self.cleaned_data['phone'] if d.isdigit())

    def clean_confirmed_email(self):
        email = self.cleaned_data.get('email')
        confimed_email = self.cleaned_data['confirmed_email']

        if email != confimed_email:
            raise forms.ValidationError(['The two email fields didn’t match.'],  code='email_match')

    def clean_clinic(self):
        clinic = self.cleaned_data['clinic'].title()
        if UserProfile.objects.filter(clinic=clinic).exists():
            raise ValidationError(_('Clinic already exists'),  code='exists_clinic')

        return clinic

    def save(self):
        super().save()
        self.instance.profile.name = self.cleaned_data['name']
        self.instance.profile.clinic = self.cleaned_data['clinic']
        self.instance.profile.role = self.cleaned_data['role']
        self.instance.profile.phone = self.cleaned_data['phone']
        self.instance.profile.cpf = self.cleaned_data['cpf']
        self.instance.profile.cnpj = self.cleaned_data['cnpj']
        self.instance.save()
        return self.instance
