from django import forms
from django.contrib.auth.forms import UserCreationForm

from web_server.core.models import CostumUser


class UserForm(UserCreationForm):

    class Meta:
        model = CostumUser
        fields = ('email', 'password1', 'password2',)


class ProfileForm(forms.ModelForm):
    ...

class SignUpForm:
    pass