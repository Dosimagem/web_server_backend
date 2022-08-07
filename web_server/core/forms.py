from django import forms
from django.contrib.auth.forms import UserCreationForm

from web_server.core.models import CustomUser


class SignupForm(UserCreationForm):

    name = forms.CharField(label='name', max_length=150)
    phone = forms.CharField(label='phone', max_length=30)
    institution = forms.CharField(label='institution', max_length=30)
    role = forms.CharField(label='role', max_length=30)

    class Meta:
        model = CustomUser
        fields = ('email', 'password1', 'password2',)

    def clean_name(self):
        return self.cleaned_data['name'].title()

    def clean_institution(self):
        return self.cleaned_data['institution'].title()

    def clean_role(self):
        return self.cleaned_data['role'].lower()

    def clean_phone(self):
        return ''.join(d for d in self.cleaned_data['phone'] if d.isdigit())

    def save(self):
        super().save()
        self.instance.profile.name = self.cleaned_data['name']
        self.instance.profile.institution = self.cleaned_data['institution']
        self.instance.profile.role = self.cleaned_data['role']
        self.instance.profile.phone = self.cleaned_data['phone']
        self.instance.save()
