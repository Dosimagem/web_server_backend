from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from web_server.isotope.models import Isotope


class IsotopeDosimetryForm(forms.Form):

    isotope = forms.CharField(max_length=6)

    def clean_isotope(self):
        isotopes_list = [isotope.name for isotope in Isotope.objects.filter(dosimetry=True)]

        isotope = self.cleaned_data['isotope']
        if isotope not in isotopes_list:
            raise ValidationError(_('Isotope not registered.'), code='invalid_isotope')

        return isotope


class IsotopeRadiosynoForm(forms.Form):

    isotope = forms.CharField(max_length=6)

    def clean_isotope(self):
        isotopes_list = [isotope.name for isotope in Isotope.objects.filter(radiosyno=True)]

        isotope = self.cleaned_data['isotope']
        if isotope not in isotopes_list:
            raise ValidationError(_('Isotope not registered.'), code='invalid_isotope')

        return isotope
