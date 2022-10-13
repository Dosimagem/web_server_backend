import os
from functools import partial
from uuid import uuid4

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, MinValueValidator
from django.db import models
from django.utils.timezone import now

from web_server.core.models import CreationModificationBase

FORMAT_DATE = '%Y-%m-%d %H:%M:%S'


class Order(CreationModificationBase, models.Model):

    CLINIC_DOSIMETRY = 'DC'
    PRECLINIC_DOSIMETRY = 'PCD'

    SERVICES_CODES = {CLINIC_DOSIMETRY: '01', PRECLINIC_DOSIMETRY: '02'}

    SERVICES_NAMES = (
        (CLINIC_DOSIMETRY, 'Dosimetria Clinica'),
        (PRECLINIC_DOSIMETRY, 'Dosimetria Preclinica'),
    )

    AWAITING_PAYMENT = 'APG'
    CONFIRMED = 'CON'

    STATUS_PAYMENT = (
        (AWAITING_PAYMENT, 'Aguardando pagamento'),
        (CONFIRMED, 'Confirmado'),
    )

    uuid = models.UUIDField(default=uuid4, editable=False, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
    )
    quantity_of_analyzes = models.PositiveIntegerField('Amount of analysis', default=0)
    remaining_of_analyzes = models.PositiveIntegerField('Remaning of analysis', default=0)
    price = models.DecimalField('Price', max_digits=14, decimal_places=2)
    status_payment = models.CharField(
        'Status payment',
        max_length=3,
        choices=STATUS_PAYMENT,
        default=AWAITING_PAYMENT,
    )
    service_name = models.CharField('Service name', max_length=3, choices=SERVICES_NAMES)
    permission = models.BooleanField('Permission', default=False)
    code = models.CharField('Code', max_length=20)

    def __str__(self):
        return self.code

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

    def is_analysis_available(self):
        return self.remaining_of_analyzes > 0

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if not self.code:
            self.code = self._generate_code()
            self.save()

    def _generate_code(self):
        clinic_id = self.user.id
        year = str(self.created_at.year)[2:]
        id = self.id
        code = self._code_service()
        return f'{clinic_id:04}.{year}/{id:04}-{code:02}'

    def _code_service(self):
        return self.SERVICES_CODES[self.service_name]


class Isotope(CreationModificationBase, models.Model):

    name = models.CharField(max_length=6, unique=True)

    def __str__(self):
        return self.name


def _timestamp(datetime):
    return str(datetime.timestamp()).replace('.', '')


def upload_to(instance, filename, type):

    datetime_now = now()
    time = _timestamp(datetime_now)

    _, extension = os.path.splitext(filename)

    if type == 'calibration':
        id = instance.user.id
    else:
        id = instance.order.user.id

    filename = f'{type}_{time}{extension}'

    return f'{id}/{filename}'


upload_calibration_to = partial(upload_to, type='calibration')
upload_clinic_dosimetry_to = partial(upload_to, type='clinic_dosimetry')
upload_preclinic_dosimetry_to = partial(upload_to, type='preclinic_dosimetry')
upload_report_to = partial(upload_to, type='report')


class Calibration(CreationModificationBase, models.Model):

    uuid = models.UUIDField(default=uuid4, editable=False, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='calibrations',
    )
    isotope = models.ForeignKey('Isotope', on_delete=models.CASCADE, related_name='calibrations')

    calibration_name = models.CharField('Calibration Name', max_length=24, validators=[MinLengthValidator(3)])
    syringe_activity = models.FloatField('Syringe Activity', validators=[MinValueValidator(0.0)])
    residual_syringe_activity = models.FloatField('Residual Syringe Activity', validators=[MinValueValidator(0.0)])
    measurement_datetime = models.DateTimeField('Measurement Datetime')
    phantom_volume = models.FloatField('Phantom Volume', validators=[MinValueValidator(0.0)])
    acquisition_time = models.FloatField('Acquisition Time', validators=[MinValueValidator(0.0)])

    images = models.FileField('Calibration Images', upload_to=upload_calibration_to, null=False)

    class Meta:
        unique_together = (
            'user',
            'calibration_name',
        )

    def __str__(self):
        return self.calibration_name

    def to_dict(self, request):
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
            'createAt': self.created_at,
            'modifiedAt': self.modified_at,
        }

        if self.images.name:
            dict_['images_url'] = request.build_absolute_uri(self.images.url)

        return dict_


class DosimetryAnalysisBase(CreationModificationBase, models.Model):

    # DATA_SENT = 'DS'
    ANALYZING_INFOS = 'AI'
    INVALID_INFOS = 'II'
    PROCESSING = 'PR'
    CONCLUDED = 'CO'

    STATUS = (
        # Data sent
        # (DATA_SENT, 'Dados enviados'),
        (ANALYZING_INFOS, 'Verificando informações'),
        (INVALID_INFOS, 'Informações inválidas'),
        (PROCESSING, 'Processando a análise'),
        (CONCLUDED, 'Análise concluída'),
    )

    uuid = models.UUIDField(default=uuid4, editable=False, unique=True)

    analysis_name = models.CharField('Analysis Name', max_length=24, validators=[MinLengthValidator(3)])

    status = models.CharField('Status', max_length=3, choices=STATUS, default=ANALYZING_INFOS)
    report = models.FileField('Report', blank=True, null=True, upload_to=upload_report_to)
    active = models.BooleanField('Active', default=True)

    injected_activity = models.FloatField('Injected Activity', validators=[MinValueValidator(0.0)])
    administration_datetime = models.DateTimeField('Administration Datetime')
    code = models.CharField('Code', max_length=30)

    class Meta:
        abstract = True

    def __str__(self):
        return self.code

    def to_dict(self, request):
        dict_ = {
            'id': self.uuid,
            'user_id': self.order.user.uuid,
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
            'administration_datetime': self.administration_datetime.strftime(FORMAT_DATE),
            'report': '',
        }

        if self.report.name:
            dict_['report'] = request.build_absolute_uri(self.report.url)

        return dict_

    def clean(self):
        if hasattr(self, 'order'):
            order = self.order
            if order.service_name != self.SERVICE_NAME_CODE:
                raise ValidationError('Este serviço não foi contratado nesse pedido.')

        if self.status == self.CONCLUDED:
            if self.report.name is None or self.report.name == '':
                raise ValidationError('É necessario anexar o relatório.')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if not self.code:
            self.code = self._generate_code()
            self.save()

    def _generate_code(self):
        raise NotImplementedError()


class ClinicDosimetryAnalysis(DosimetryAnalysisBase):

    SERVICE_NAME_CODE = Order.CLINIC_DOSIMETRY
    CODE = Order.SERVICES_CODES[SERVICE_NAME_CODE]

    # user = models.ForeignKey('core.CustomUser',
    #                          on_delete=models.CASCADE,
    #                          related_name='clinic_dosimetry_analysis')
    calibration = models.ForeignKey(
        'Calibration',
        on_delete=models.CASCADE,
        related_name='clinic_dosimetry_analysis',
    )
    order = models.ForeignKey(
        'Order',
        on_delete=models.CASCADE,
        related_name='clinic_dosimetry_analysis',
    )
    images = models.FileField('Images', upload_to=upload_clinic_dosimetry_to)

    class Meta:
        db_table = 'clinic_dosimetry_analysis'
        verbose_name = 'Clinic Dosimetry'
        verbose_name_plural = 'Clinic Dosimetries'
        unique_together = (
            'order',
            'analysis_name',
        )

    def _generate_code(self):
        clinic_id = self.order.user.pk
        year = str(self.created_at.year)[2:]
        isotope = self.calibration.isotope
        order_id = self.order.pk
        id = self.pk
        code = self.CODE
        return f'{clinic_id:04}.{isotope}.{year}.{order_id:04}/{id:04}-{code:02}'


class PreClinicDosimetryAnalysis(DosimetryAnalysisBase):

    SERVICE_NAME_CODE = Order.PRECLINIC_DOSIMETRY
    CODE = Order.SERVICES_CODES[SERVICE_NAME_CODE]

    # user = models.ForeignKey('core.CustomUser',
    #                          on_delete=models.CASCADE,
    #                          related_name='preclinic_dosimetry_analysis')
    calibration = models.ForeignKey(
        'Calibration',
        on_delete=models.CASCADE,
        related_name='preclinic_dosimetry_analysis',
    )
    order = models.ForeignKey(
        'Order',
        on_delete=models.CASCADE,
        related_name='preclinic_dosimetry_analysis',
    )

    images = models.FileField('Images', upload_to=upload_preclinic_dosimetry_to)

    class Meta:
        db_table = 'preclinic_dosimetry_analysis'
        verbose_name = 'Preclinic Dosimetry'
        verbose_name_plural = 'Preclinic Dosimetries'
        unique_together = (
            'order',
            'analysis_name',
        )

    def _generate_code(self):
        clinic_id = self.order.user.pk
        year = str(self.created_at.year)[2:]
        isotope = self.calibration.isotope
        order_id = self.order.pk
        id = self.pk
        code = self.CODE
        return f'{clinic_id:04}.{isotope}.{year}.{order_id:04}/{id:04}-{code:02}'
