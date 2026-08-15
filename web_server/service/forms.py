from django import forms
from django.forms import ValidationError
from django.utils.translation import gettext as _

from web_server.isotope.forms import IsotopeRadiosynoForm
from web_server.service.archive_utils import validate_and_sanitize_archive
from web_server.service.models import (
    Calibration,
    ClinicDosimetryAnalysis,
    Order,
    PreClinicDosimetryAnalysis,
    RadiosynoAnalysis,
    SegmentationAnalysis,
)


class SecureCompressedImagesFormMixin:
    def clean_images(self):
        images = self.cleaned_data.get('images')
        if not images:
            return images
        from django.db.models.fields.files import FieldFile
        if isinstance(images, FieldFile):
            return images
        return validate_and_sanitize_archive(images)


class CreateOrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = (
            'user',
            'quantity_of_analyzes',
            'remaining_of_analyzes',
            'price',
            'service_name',
            'equipment_type',
            'equipment_modality',
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


class CreateCalibrationForm(SecureCompressedImagesFormMixin, forms.ModelForm):
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


class ClinicDosimetryAnalysisCreateForm(SecureCompressedImagesFormMixin, forms.ModelForm):
    class Meta:
        model = ClinicDosimetryAnalysis
        fields = (
            'calibration',
            'order',
            'images',
            'analysis_name',
            'injected_activity',
            'administration_datetime',
            'isotope',
        )

    def clean(self):
        cleaned_data = super().clean()
        order = cleaned_data.get('order')
        calibration = cleaned_data.get('calibration')
        isotope = cleaned_data.get('isotope')

        if order:
            if order.requires_calibration and not calibration:
                self.add_error('calibration', _('This field is required.'))
            elif not order.requires_calibration and not isotope:
                self.add_error('isotope', _('This field is required.'))

        return cleaned_data


class ClinicDosimetryAnalysisUpdateForm(ClinicDosimetryAnalysisCreateForm):
    def change_status_and_save(self):
        self.instance.status = ClinicDosimetryAnalysis.Status.DATA_SENT
        super().save()
        return self.instance


class PreClinicDosimetryAnalysisCreateForm(SecureCompressedImagesFormMixin, forms.ModelForm):
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
    calibration_id = forms.UUIDField(required=False)
    isotope = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        self.requires_calibration = kwargs.pop('requires_calibration', True)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        calibration_id = cleaned_data.get('calibration_id')
        isotope = cleaned_data.get('isotope')

        if self.requires_calibration:
            if 'calibration_id' not in self.errors and not calibration_id:
                self.add_error('calibration_id', _('This field is required.'))
        else:
            if 'isotope' not in self.errors and not isotope:
                self.add_error('isotope', _('This field is required.'))

        return cleaned_data


class PreClinicAndClinicDosimetryAnalysisUpdateFormApi(PreClinicAndClinicDosimetryAnalysisCreateFormApi):
    ...


class RadiosynoAnalysisCreateFormApi(IsotopeRadiosynoForm):
    ...


class RadiosynoAnalysisUpdateFormApi(RadiosynoAnalysisCreateFormApi):
    ...


class SegmentationAnalysisCreateForm(SecureCompressedImagesFormMixin, forms.ModelForm):
    class Meta:
        model = SegmentationAnalysis
        fields = ('order', 'analysis_name', 'images')


class SegmentationAnalysisUpdateForm(SegmentationAnalysisCreateForm):
    def change_status_and_save(self):
        self.instance.status = SegmentationAnalysis.Status.DATA_SENT
        super().save()
        return self.instance


class RadiosynoAnalysisCreateForm(SecureCompressedImagesFormMixin, forms.ModelForm):
    class Meta:
        model = RadiosynoAnalysis
        fields = ('order', 'analysis_name', 'images', 'isotope')


class RadiosynoAnalysisUpdateForm(RadiosynoAnalysisCreateForm):
    def change_status_and_save(self):
        self.instance.status = RadiosynoAnalysis.Status.DATA_SENT
        super().save()
        return self.instance
