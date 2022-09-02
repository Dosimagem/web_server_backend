from django import forms
from django.forms import ValidationError
from django.utils.translation import gettext as _

from web_server.service.models import Order


class CreateOrderForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = ('user',
                  'quantity_of_analyzes',
                  'remaining_of_analyzes',
                  'service_name',
                  'price',
                  'service_name',
                  'status_payment',
                  'permission')

    def clean_remaining_of_analyzes(self):

        quantity_of_analyzes = self.cleaned_data.get('quantity_of_analyzes')
        remaining_of_analyzes = self.cleaned_data.get('remaining_of_analyzes')

        if (quantity_of_analyzes is not None) and (remaining_of_analyzes > quantity_of_analyzes):
            raise ValidationError(
                _('Must be lower with the field quantity of analyzes.'),
                code='invalid')

        return remaining_of_analyzes
