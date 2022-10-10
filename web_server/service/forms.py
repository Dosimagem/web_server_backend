from django import forms
from django.forms import ValidationError
from django.utils.translation import gettext as _

from web_server.service.models import (
                                      ClinicDosimetryAnalysis,
                                      PreClinicDosimetryAnalysis,
                                      Isotope,
                                      Order,
                                      Calibration,
                                      )


class CreateOrderForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = ('user',
                  'quantity_of_analyzes',
                  'remaining_of_analyzes',
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
                code='lower_or_equal')

        return remaining_of_analyzes


class CreateCalibrationForm(forms.ModelForm):

    class Meta:
        model = Calibration
        fields = ('user',
                  'isotope',
                  'calibration_name',
                  'syringe_activity',
                  'residual_syringe_activity',
                  'measurement_datetime',
                  'phantom_volume',
                  'acquisition_time',
                  'images')


class UpdateCalibrationForm(CreateCalibrationForm):
    ...


class IsotopeForm(forms.Form):

    isotope = forms.CharField(max_length=6)

    def clean_isotope(self):
        isotopes_list = [isotope.name for isotope in Isotope.objects.all()]

        isotope = self.cleaned_data['isotope']
        if isotope not in isotopes_list:
            raise ValidationError(_('Isotope not registered.'), code='invalid_isotope')

        return isotope


class ClinicDosimetryAnalysisCreateForm(forms.ModelForm):

    class Meta:
        model = ClinicDosimetryAnalysis
        fields = ('user',
                  'calibration',
                  'order',
                  'images',
                  'analysis_name',
                  'injected_activity',
                  'administration_datetime')


class ClinicDosimetryAnalysisUpdateForm(ClinicDosimetryAnalysisCreateForm):
    def change_status_and_save(self):
        self.instance.status = ClinicDosimetryAnalysis.ANALYZING_INFOS
        super().save()
        return self.instance


class PreClinicDosimetryAnalysisCreateForm(forms.ModelForm):

    class Meta:
        model = PreClinicDosimetryAnalysis
        fields = ('user',
                  'calibration',
                  'order',
                  'images',
                  'analysis_name',
                  'injected_activity',
                  'administration_datetime')


class PreClinicDosimetryAnalysisUpdateForm(PreClinicDosimetryAnalysisCreateForm):
    def change_status_and_save(self):
        self.instance.status = PreClinicDosimetryAnalysis.ANALYZING_INFOS
        super().save()
        return self.instance


class PreClinicAndClinicDosimetryAnalysisCreateFormApi(forms.Form):
    calibration_id = forms.UUIDField()


class PreClinicAndClinicDosimetryAnalysisUpdateFormApi(PreClinicAndClinicDosimetryAnalysisCreateFormApi):
    ...
