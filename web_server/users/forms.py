from django.contrib.auth.forms import UserCreationForm

from web_server.users.models import CostumUser


class SignUpForm(UserCreationForm):

    class Meta:
        model = CostumUser
        fields = ('username', 'email', 'phone', 'institution', 'role', 'password1', 'password2',)
