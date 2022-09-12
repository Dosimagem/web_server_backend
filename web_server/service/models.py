from functools import partial
import os
from uuid import uuid4

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils.timezone import now
from django.utils.text import slugify


class Order(models.Model):

    DOSIMETRY_CLINIC = 'DC'
    DOSIMETRY_PRECLINIC = 'DPC'

    SERVICES_TYPES = (
        (DOSIMETRY_CLINIC, 'Dosimetria Clinica'),
        (DOSIMETRY_PRECLINIC, 'Dosimetria Preclinica')
    )

    AWAITING_PAYMENT = 'APG'
    CONFIRMED = 'CON'
    ANALYSIS = 'ALY'

    STATUS_PAYMENT = (
        (AWAITING_PAYMENT, 'Aguardando pagamento'),
        (CONFIRMED, 'Confirmado'),
        (ANALYSIS, 'Analise'),
    )

    uuid = models.UUIDField(default=uuid4, editable=False, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    quantity_of_analyzes = models.PositiveIntegerField('Amount of analysis', default=0)
    remaining_of_analyzes = models.PositiveIntegerField('Remaning of analysis', default=0)
    price = models.DecimalField('Price', max_digits=14, decimal_places=2)
    status_payment = models.CharField('Status payment', max_length=3, choices=STATUS_PAYMENT, default=AWAITING_PAYMENT)
    service_name = models.CharField('Service name', max_length=3, choices=SERVICES_TYPES)
    permission = models.BooleanField('Permission', default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.profile.name

    class Meta:
        verbose_name = 'User Order'
        verbose_name_plural = 'User Orders'

    # def save(self, *args, **kwargs):
    #     if self.remaining_of_analyzes > self.quantity_of_analyzes:
    #         raise ValidationError(
    #             _('Remaining of analyzes must be lower or equal quantity of analyzes.'),
    #             code='invalid')  # TODO: ValidationError or IntegrityError
    #     super().save(*args, **kwargs)


class Isotope(models.Model):

    name = models.CharField(max_length=6)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


def _timestamp(datetime):
    return str(datetime.timestamp()).replace('.', '')


def upload_to(instance, filename, type):

    datetime_now = now()
    time = _timestamp(datetime_now)

    _, extension = os.path.splitext(filename)

    if type == 'calibrations':
        slug_calibration_name = slugify(instance.calibration_name)
        slug_clinic_name = slugify(instance.user.profile.clinic)
        filename = f'{slug_calibration_name}_{time}{extension}'
        return f'{slug_clinic_name}/{type}/{filename}'

    return filename


upload_calibration_to = partial(upload_to, type='calibrations')


class Calibration(models.Model):

    uuid = models.UUIDField(default=uuid4, editable=False, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='calibrations')
    isotope = models.ForeignKey('Isotope', on_delete=models.CASCADE, related_name='calibrations')

    calibration_name = models.CharField('Calibration Name', max_length=24)
    syringe_activity = models.FloatField('Syringe Activity', validators=[MinValueValidator(0.0)])
    residual_syringe_activity = models.FloatField('Residual Syringe Activity', validators=[MinValueValidator(0.0)])
    measurement_datetime = models.DateTimeField('Measurement Datetime')
    phantom_volume = models.FloatField('Phantom Volume', validators=[MinValueValidator(0.0)])
    acquisition_time = models.FloatField('Acquisition Time', validators=[MinValueValidator(0.0)])

    images = models.FileField('Calibration Images', upload_to=upload_calibration_to, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'calibration_name',)

    def __str__(self):
        return self.calibration_name

    def to_dict(self):
        return {
            'id': self.uuid,
            'user_id': self.user.uuid,
            'isotope': self.isotope.name,
            'calibration_name': self.calibration_name,
            'syringe_activity': self.syringe_activity,
            'residual_syringe_activity': self.residual_syringe_activity,
            'measurement_datetime': self.measurement_datetime.strftime('%d/%m/%Y - %H:%M:%S'),
            'phantom_volume': self.phantom_volume,
            'acquisition_time': self.acquisition_time,
        }

# upload_report_to = partial(upload_to, type='report')


# class BaseAbstractOrder(models.Model):

#     AWAITING_PAYMENT = 'APG'
#     AWAITTING_PROCESSING = 'APR'
#     PROCESSING = 'PRC'
#     CONCLUDED = 'CON'

#     STATUS = (
#         (AWAITING_PAYMENT, 'Aguardando pagamento'),
#         (AWAITTING_PROCESSING, 'Aguardando processamento'),
#         (PROCESSING, 'Processando'),
#         (CONCLUDED, 'Concluído'),
#     )

#     def save(self, *args, **kwargs):
#         if not self.total_price:
#             self.total_price = self.service.unit_price * self.amount
#         super().save(*args, **kwargs)

#     requester = models.ForeignKey('core.CustomUser', on_delete=models.CASCADE)
#     service = models.ForeignKey('Service', on_delete=models.CASCADE)
#     amount = models.IntegerField('Amount')

#     status = models.CharField('status', max_length=3, choices=STATUS, default=AWAITING_PAYMENT)

#     # this field is automatically filled in by amount and unit price of the service
#     total_price = models.DecimalField('Total price', max_digits=14, decimal_places=2, null=True, blank=True)

#     report = models.FileField('Report', upload_to=upload_report_to, blank=True)

#     created_at = models.DateTimeField(auto_now_add=True)
#     modified_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         abstract = True

#     def get_path_report(self):
#         return str(self.report)


# class DosimetryOrder(BaseAbstractOrder):

#     CLINICAL = 'C'
#     PRECLINICAL = 'P'

#     TYPES = (
#         (CLINICAL, 'Clinical'),
#         (PRECLINICAL, 'Pre Clinical'),
#     )

#     # this field is automatically filled in by service name
#     type = models.CharField('Dosimetry Type', max_length=1, choices=TYPES, blank=True)
#     camera_factor = models.FloatField('Camera Factor')
#     radionuclide = models.CharField('Radionuclide', max_length=6)
#     injected_activity = models.FloatField('Injected Activity')
#     injection_datetime = models.DateTimeField('Injection datetime')
#     images = models.FileField('Images', upload_to=upload_img_to)

#     def save(self, *args, **kwargs):
#         if not self.type:
#             if 'preclinica' in self.service.name.lower():
#                 self.type = self.PRECLINICAL
#             else:
#                 self.type = self.CLINICAL

#         super().save(*args, **kwargs)

#     def __str__(self):
#         msg = ''
#         if self.type == self.CLINICAL:
#             msg = f'Clinical Dosimetry (id={self.pk})'
#         elif self.type == self.PRECLINICAL:
#             msg = f'Preclinical Dosimetry (id={self.pk})'

#         return msg


# class SegmentationOrder(BaseAbstractOrder):
#     images = models.FileField('Images', upload_to=upload_img_to)
#     observations = models.TextField('Obeservations', max_length=5000)

#     def __str__(self):
#         return f'Segmentantion (id={self.pk})'


# class ComputationalModelOrder(BaseAbstractOrder):

#     CT = 'C'
#     SPECT = 'S'

#     OPTIONS = (
#         (CT, 'CT'),
#         (SPECT, 'SPECT'),
#     )

#     images = models.FileField('Images', upload_to=upload_img_to)
#     equipment_specification = models.CharField('Equipment Specification', max_length=1, choices=OPTIONS)

#     def __str__(self):
#         return f'Computational Modeling (id={self.pk})'
