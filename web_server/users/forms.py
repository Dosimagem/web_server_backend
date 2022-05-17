from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignUpForm(UserCreationForm):
    phone = forms.CharField(help_text='Required.')
    institution = forms.CharField(help_text='Required.')
    role = forms.CharField(help_text='Required.')

    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'institution', 'role', 'password1', 'password2', )
