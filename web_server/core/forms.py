from django.contrib.auth.forms import UserCreationForm

from web_server.core.models import CostumUser


class SignUpForm(UserCreationForm):

    class Meta:
        model = CostumUser
        fields = ('name', 'email', 'phone', 'institution', 'role', 'password1', 'password2',)
