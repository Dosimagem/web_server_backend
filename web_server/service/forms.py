from django import forms
from django.forms import ValidationError
from django.utils.translation import gettext as _

from web_server.service.models import (
    Calibration,
    ClinicDosimetryAnalysis,
    Isotope,
    IsotopeRadiosyno,
    Order,
    PreClinicDosimetryAnalysis,
    RadiosynoAnalysis,
    SegmentationAnalysis,
)


class CreateOrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = (
            'user',
            'quantity_of_analyzes',
            'remaining_of_analyzes',
            'price',
            'service_name',
            'status_payment',
            'active',
        )

    def clean_remaining_of_analyzes(self):

        quantity_of_analyzes = self.cleaned_data.get('quantity_of_analyzes')
        remaining_of_analyzes = self.cleaned_data.get('remaining_of_analyzes')

        if (quantity_of_analyzes is not None) and (remaining_of_analyzes > quantity_of_analyzes):
            raise ValidationError(
                _('The remaining analysis must be less than the analysis field number.'),
                code='lower_or_equal',
            )

        return remaining_of_analyzes


class CreateCalibrationForm(forms.ModelForm):
    class Meta:
        model = Calibration
        fields = (
            'user',
            'isotope',
            'calibration_name',
            'syringe_activity',
            'residual_syringe_activity',
            'measurement_datetime',
            'phantom_volume',
            'acquisition_time',
            'images',
        )


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
        fields = (
            'calibration',
            'order',
            'images',
            'analysis_name',
            'injected_activity',
            'administration_datetime',
        )


class ClinicDosimetryAnalysisUpdateForm(ClinicDosimetryAnalysisCreateForm):
    def change_status_and_save(self):
        self.instance.status = ClinicDosimetryAnalysis.Status.DATA_SENT
        super().save()
        return self.instance


class PreClinicDosimetryAnalysisCreateForm(forms.ModelForm):
    class Meta:
        model = PreClinicDosimetryAnalysis
        fields = (
            'calibration',
            'order',
            'images',
            'analysis_name',
            'injected_activity',
            'administration_datetime',
        )


class PreClinicDosimetryAnalysisUpdateForm(PreClinicDosimetryAnalysisCreateForm):
    def change_status_and_save(self):
        self.instance.status = PreClinicDosimetryAnalysis.Status.DATA_SENT
        super().save()
        return self.instance


class PreClinicAndClinicDosimetryAnalysisCreateFormApi(forms.Form):
    calibration_id = forms.UUIDField()


class PreClinicAndClinicDosimetryAnalysisUpdateFormApi(PreClinicAndClinicDosimetryAnalysisCreateFormApi):
    ...


class RadiosynoAnalysisCreateFormApi(IsotopeForm):
    def clean_isotope(self):
        isotopes_list = [isotope.name for isotope in IsotopeRadiosyno.objects.all()]

        isotope = self.cleaned_data['isotope']
        if isotope not in isotopes_list:
            raise ValidationError(_('Isotope not registered.'), code='invalid_isotope')

        return isotope


class RadiosynoAnalysisUpdateFormApi(RadiosynoAnalysisCreateFormApi):
    ...


class SegmentationAnalysisCreateForm(forms.ModelForm):
    class Meta:
        model = SegmentationAnalysis
        fields = ('order', 'analysis_name', 'images')


class SegmentationAnalysisUpdateForm(SegmentationAnalysisCreateForm):
    def change_status_and_save(self):
        self.instance.status = SegmentationAnalysis.Status.DATA_SENT
        super().save()
        return self.instance


class RadiosynoAnalysisCreateForm(forms.ModelForm):
    class Meta:
        model = RadiosynoAnalysis
        fields = ('order', 'analysis_name', 'images', 'isotope')


class RadiosynoAnalysisUpdateForm(RadiosynoAnalysisCreateForm):
    def change_status_and_save(self):
        self.instance.status = RadiosynoAnalysis.Status.DATA_SENT
        super().save()
        return self.instance
