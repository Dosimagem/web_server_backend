from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import ValidationError
from django.utils.translation import gettext as _
from django.contrib.auth import get_user_model

from web_server.core.models import CustomUser, UserProfile


User = get_user_model()


class ProfileCreateForm(forms.ModelForm):

    class Meta:
        model = UserProfile
        fields = ('user', 'name', 'phone', 'clinic', 'role', 'cpf', 'cnpj', )

    def clean_name(self):
        return self.cleaned_data['name'].title()

    def clean_role(self):
        return self.cleaned_data['role'].lower()

    # TODO: Verficar depois se o nome da clinica e cnpj precisa ser unicos.

    def _unique(self, field, msg_error):
        instance = self.instance

        queryset = UserProfile.objects.filter(**field)

        if instance is not None:
            if queryset.exclude(id=instance.id).exists():
                raise ValidationError(msg_error,  code='exists')
        else:
            if queryset.exists():
                raise ValidationError(msg_error,  code='exists')

    def clean_cpf(self):

        cpf = self.cleaned_data['cpf']

        self._unique({'cpf': cpf}, _('CPF already exists'))

        return cpf

    def clean_clinic(self):

        clinic = self.cleaned_data['clinic'].title()

        # TODO: Should the clinic name be unique?
        # self._unique({'clinic': clinic}, _('Clinic already exists'))

        return clinic

    # TODO: Should the CNPJ be unique?
    # def clean_cnpj(self):

    #     cnpj = self.cleaned_data['cnpj']

    #     self._unique({'cnpj': cnpj}, _('CNPJ already exists'))

    #     return cnpj


class ProfileUpdateForm(ProfileCreateForm):

    class Meta:
        model = UserProfile
        fields = ('name', 'clinic', 'role', 'cnpj', )


class MyUserCreationForm(UserCreationForm):

    confirmed_email = forms.EmailField(label='confirmed_email')

    class Meta:
        model = CustomUser
        fields = ('email', 'password1', 'password2',)

    def clean_confirmed_email(self):
        email = self.cleaned_data.get('email')
        confimed_email = self.cleaned_data['confirmed_email']

        if email != confimed_email:
            raise forms.ValidationError(['The two email fields didn’t match.'],  code='email_match')


# TODO: Testar de forma unitaria o form.
class UpdateEmailForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('email',)
