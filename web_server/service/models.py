from functools import partial
import os
from uuid import uuid4

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils.timezone import now
from django.core.exceptions import ValidationError

from web_server.core.models import CreationModificationBase


FORMAT_DATE = '%Y-%m-%d %H:%M:%S'


class Order(CreationModificationBase, models.Model):

    CLINIC_DOSIMETRY = 'DC'
    PRECLINIC_DOSIMETRY = 'PCD'

    SERVICES_NAMES = (
        (CLINIC_DOSIMETRY, 'Dosimetria Clinica'),
        (PRECLINIC_DOSIMETRY, 'Dosimetria Preclinica')
    )

    AWAITING_PAYMENT = 'APG'
    CONFIRMED = 'CON'

    STATUS_PAYMENT = (
        (AWAITING_PAYMENT, 'Aguardando pagamento'),
        (CONFIRMED, 'Confirmado'),
    )

    uuid = models.UUIDField(default=uuid4, editable=False, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    quantity_of_analyzes = models.PositiveIntegerField('Amount of analysis', default=0)
    remaining_of_analyzes = models.PositiveIntegerField('Remaning of analysis', default=0)
    price = models.DecimalField('Price', max_digits=14, decimal_places=2)
    status_payment = models.CharField('Status payment', max_length=3, choices=STATUS_PAYMENT, default=AWAITING_PAYMENT)
    service_name = models.CharField('Service name', max_length=3, choices=SERVICES_NAMES)
    permission = models.BooleanField('Permission', default=False)

    def __str__(self):
        return f'{self.user.profile.clinic} <{self.get_service_name_display()}>'

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

    def is_analysis_available(self):
        return self.remaining_of_analyzes > 0


class Isotope(CreationModificationBase, models.Model):

    name = models.CharField(max_length=6)

    def __str__(self):
        return self.name


def _timestamp(datetime):
    return str(datetime.timestamp()).replace('.', '')


def upload_to(instance, filename, type):

    datetime_now = now()
    time = _timestamp(datetime_now)

    _, extension = os.path.splitext(filename)

    id = instance.user.id
    filename = f'{type}_{time}{extension}'

    return f'{id}/{filename}'


upload_calibration_to = partial(upload_to, type='calibration')
upload_clinic_dosimetry_to = partial(upload_to, type='clinic_dosimetry')
upload_preclinic_dosimetry_to = partial(upload_to, type='preclinic_dosimetry')
upload_report_to = partial(upload_to, type='report')


class Calibration(CreationModificationBase, models.Model):

    uuid = models.UUIDField(default=uuid4, editable=False, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='calibrations')
    isotope = models.ForeignKey('Isotope', on_delete=models.CASCADE, related_name='calibrations')

    calibration_name = models.CharField('Calibration Name', max_length=24)
    syringe_activity = models.FloatField('Syringe Activity', validators=[MinValueValidator(0.0)])
    residual_syringe_activity = models.FloatField('Residual Syringe Activity', validators=[MinValueValidator(0.0)])
    measurement_datetime = models.DateTimeField('Measurement Datetime')
    phantom_volume = models.FloatField('Phantom Volume', validators=[MinValueValidator(0.0)])
    acquisition_time = models.FloatField('Acquisition Time', validators=[MinValueValidator(0.0)])

    images = models.FileField('Calibration Images', upload_to=upload_calibration_to, null=False)

    class Meta:
        unique_together = ('user', 'calibration_name',)

    def __str__(self):
        return self.calibration_name

    def to_dict(self, request):
        # TODO: Clocar da data de criação e modificação
        dict_ = {
            'id': self.uuid,
            'user_id': self.user.uuid,
            'isotope': self.isotope.name,
            'calibration_name': self.calibration_name,
            'syringe_activity': self.syringe_activity,
            'residual_syringe_activity': self.residual_syringe_activity,
            'measurement_datetime': self.measurement_datetime.strftime(FORMAT_DATE),
            'phantom_volume': self.phantom_volume,
            'acquisition_time': self.acquisition_time,
        }

        if self.images.name:
            dict_['images_url'] = request.build_absolute_uri(self.images.url)

        return dict_


class DosimetryAnalysisBase(CreationModificationBase, models.Model):

    ANALYZING_INFOS = 'AP'
    ERRORS_ANALYZING = 'EA'
    PROCESSING = 'PR'
    CONCLUDED = 'CO'

    STATUS = (
        (ANALYZING_INFOS, 'Verificando informações'),
        (ERRORS_ANALYZING, 'Informações inválidas'),
        (PROCESSING, 'Processando a análise'),
        (CONCLUDED, 'Analise conluída'),
    )

    uuid = models.UUIDField(default=uuid4, editable=False, unique=True)

    analysis_name = models.CharField('Analysis Name', max_length=24)

    status = models.CharField('Status', max_length=3, choices=STATUS, default=ANALYZING_INFOS)
    report = models.FileField('Report', blank=True, null=True, upload_to=upload_report_to)
    active = models.BooleanField('Active', default=True)

    injected_activity = models.FloatField('Injected Activity', validators=[MinValueValidator(0.0)])
    administration_datetime = models.DateTimeField('Administration Datetime')

    class Meta:
        abstract = True

    def __str__(self):
        infos = self._infos()
        # TODO:  Falta fazer a logica do 0001
        return f'{infos["clinic"]:04}.{infos["isotope"]}.{infos["year"]}/0001-{self.CODE}'

    def _infos(self):
        clinic = self.user.profile.id
        isotope = self.calibration.isotope.name.replace('-', '')
        year = str(self.created_at.year)[2:]
        return {'clinic': clinic, 'isotope': isotope, 'year': year}

    def to_dict(self, request):
        dict_ = {
            'id': self.uuid,
            'user_id': self.user.uuid,
            'order_id': self.order.uuid,
            'calibration_id': self.calibration.uuid,
            'status': self.get_status_display(),
            'images_url': request.build_absolute_uri(self.images.url),
            'active': self.active,
            'service_name': self.order.get_service_name_display(),
            'created_at': self.created_at.strftime(FORMAT_DATE),
            'modified_at': self.modified_at.strftime(FORMAT_DATE),
            'injected_activity': self.injected_activity,
            'analysis_name': self.analysis_name,
            'administration_datetime': self.administration_datetime.strftime(FORMAT_DATE)
        }

        if self.report.name:
            dict_['report'] = request.build_absolute_uri(self.report.url)

        return dict_

    def clean(self):
        if hasattr(self, 'order'):
            order = self.order
            if order.service_name != self.SERVICE_NAME_CODE:
                raise ValidationError('Este serviço não foi contratado nesse pedido.')


class ClinicDosimetryAnalysis(DosimetryAnalysisBase):

    CODE = 1
    SERVICE_NAME_CODE = Order.CLINIC_DOSIMETRY

    user = models.ForeignKey('core.CustomUser',
                             on_delete=models.CASCADE,
                             related_name='clinic_dosimetry_analysis')
    calibration = models.ForeignKey('Calibration',
                                    on_delete=models.CASCADE,
                                    related_name='clinic_dosimetry_analysis')
    order = models.ForeignKey('Order',
                              on_delete=models.CASCADE,
                              related_name='clinic_dosimetry_analysis')
    images = models.FileField('Images', upload_to=upload_clinic_dosimetry_to)

    class Meta:
        db_table = 'clinic_dosimetry_analyis'
        verbose_name = 'Clinic Dosimetry'
        verbose_name_plural = 'Clinic Dosimetries'
        unique_together = ('order', 'analysis_name',)


class PreClinicDosimetryAnalysis(DosimetryAnalysisBase):

    CODE = 2
    SERVICE_NAME_CODE = Order.PRECLINIC_DOSIMETRY

    user = models.ForeignKey('core.CustomUser',
                             on_delete=models.CASCADE,
                             related_name='preclinic_dosimetry_analysis')
    calibration = models.ForeignKey('Calibration',
                                    on_delete=models.CASCADE,
                                    related_name='preclinic_dosimetry_analysis')
    order = models.ForeignKey('Order',
                              on_delete=models.CASCADE,
                              related_name='preclinic_dosimetry_analysis')

    images = models.FileField('Images', upload_to=upload_preclinic_dosimetry_to)

    class Meta:
        db_table = 'preclinic_dosimetry_analyis'
        verbose_name = 'Preclinic Dosimetry'
        verbose_name_plural = 'Preclinic Dosimetries'
        unique_together = ('order', 'analysis_name',)
