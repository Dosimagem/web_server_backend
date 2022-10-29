import os
from functools import partial
from uuid import uuid4

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, MinValueValidator
from django.db import models
from django.utils.text import slugify
from django.utils.timezone import now

from web_server.core.models import CreationModificationBase

FORMAT_DATE = '%Y-%m-%d %H:%M:%S'


class Order(CreationModificationBase):
    class ServicesName(models.TextChoices):
        CLINIC_DOSIMETRY = (
            'DC',
            'Dosimetria Clinica',
        )
        PRECLINIC_DOSIMETRY = (
            'PCD',
            'Dosimetria Preclinica',
        )
        SEGMENTANTION_QUANTIFICATION = (
            'SQ',
            'Segmentaçao e Quantificação',
        )
        RADIOSYNOVIORTHESIS = (
            'RA',
            'Radiosinoviortese',
        )

    class PaymentStatus(models.TextChoices):
        AWAITING_PAYMENT = (
            'APG',
            'Aguardando pagamento',
        )
        CONFIRMED = (
            'CON',
            'Confirmado',
        )

    SERVICES_CODES = {
        ServicesName.CLINIC_DOSIMETRY.value: '01',
        ServicesName.PRECLINIC_DOSIMETRY.value: '02',
        ServicesName.SEGMENTANTION_QUANTIFICATION.value: '03',
        ServicesName.RADIOSYNOVIORTHESIS.value: '04',
    }

    uuid = models.UUIDField(default=uuid4, editable=False, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    quantity_of_analyzes = models.PositiveIntegerField('Amount of analysis', default=0)
    remaining_of_analyzes = models.PositiveIntegerField('Remaning of analysis', default=0)
    price = models.DecimalField('Price', max_digits=14, decimal_places=2)
    status_payment = models.CharField(
        'Status payment', max_length=3, choices=PaymentStatus.choices, default=PaymentStatus.AWAITING_PAYMENT
    )
    service_name = models.CharField('Service name', max_length=3, choices=ServicesName.choices)
    permission = models.BooleanField('Permission', default=False)
    code = models.CharField('Code', max_length=20)

    def __str__(self):
        return self.code

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']

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
        return f'{clinic_id:04}.{year}/{id:04}-{code}'

    def _code_service(self):
        return self.SERVICES_CODES[self.service_name]


class Isotope(CreationModificationBase):

    name = models.CharField(max_length=6, unique=True)

    def __str__(self):
        return self.name


def _timestamp(datetime):

    return datetime.strftime('%d%m%y%H%M%S')


def upload_to(instance, filename, type):

    datetime_now = now()
    time = _timestamp(datetime_now)

    _, extension = os.path.splitext(filename)

    if type == 'calibration':
        id = instance.user.id
        prefix = f'{id}'
    else:
        id = instance.order.user.id
        order_code = slugify(instance.order.code)
        number = instance.order.quantity_of_analyzes - instance.order.remaining_of_analyzes + 1
        prefix = f'{id}/{order_code}/{number}'

    filename = f'{type}_{time}{extension}'

    return f'{prefix}/{filename}'


upload_calibration_to = partial(upload_to, type='calibration')
upload_clinic_dosimetry_to = partial(upload_to, type='clinic_dosimetry')
upload_preclinic_dosimetry_to = partial(upload_to, type='preclinic_dosimetry')
upload_segmentation_analysis_to = partial(upload_to, type='segmentation_analysis')
upload_radiosyno_analysis_to = partial(upload_to, type='radiosyno_analysis')
upload_report_to = partial(upload_to, type='report')


class Calibration(CreationModificationBase):

    uuid = models.UUIDField(default=uuid4, editable=False, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='calibrations')
    isotope = models.ForeignKey('Isotope', on_delete=models.CASCADE, related_name='calibrations')

    calibration_name = models.CharField('Calibration Name', max_length=24, validators=[MinLengthValidator(3)])
    syringe_activity = models.FloatField('Syringe Activity', validators=[MinValueValidator(0.0)])
    residual_syringe_activity = models.FloatField('Residual Syringe Activity', validators=[MinValueValidator(0.0)])
    measurement_datetime = models.DateTimeField('Measurement Datetime')
    phantom_volume = models.FloatField('Phantom Volume', validators=[MinValueValidator(0.0)])
    acquisition_time = models.FloatField('Acquisition Time', validators=[MinValueValidator(0.0)])

    images = models.FileField('Calibration Images', upload_to=upload_calibration_to, null=False)

    class Meta:
        unique_together = ('user', 'calibration_name')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.calibration_name} - {self.user}'

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


class AnalysisBase(CreationModificationBase):
    class Status(models.TextChoices):
        DATA_SENT = (
            'DS',
            'Dados enviados',
        )
        ANALYZING_INFOS = (
            'AI',
            'Verificando informações',
        )
        INVALID_INFOS = (
            'II',
            'Informações inválidas',
        )
        PROCESSING = (
            'PR',
            'Processando a análise',
        )
        CONCLUDED = (
            'CO',
            'Análise concluída',
        )

    uuid = models.UUIDField(default=uuid4, editable=False, unique=True)

    analysis_name = models.CharField('Analysis Name', max_length=24, validators=[MinLengthValidator(3)])

    status = models.CharField('Status', max_length=3, choices=Status.choices, default=Status.DATA_SENT)
    report = models.FileField('Report', blank=True, null=True, upload_to=upload_report_to)
    active = models.BooleanField('Active', default=True)

    code = models.CharField('Code', max_length=30)

    message_to_user = models.TextField('Message to user', default='', blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.code

    def clean(self):
        if hasattr(self, 'order'):
            order = self.order
            if order.service_name != self.SERVICE_NAME_CODE:
                raise ValidationError('Este serviço não foi contratado nesse pedido.')

        if self.status == self.Status.CONCLUDED:
            if self.report.name is None or self.report.name == '':
                raise ValidationError('É necessario anexar o relatório.')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if not self.code:
            self.code = self._generate_code()
            self.save()

    def _generate_code(self):
        raise NotImplementedError()

    def to_dict(self, request):
        dict_ = {
            'id': self.uuid,
            'user_id': self.order.user.uuid,
            'order_id': self.order.uuid,
            'status': self.get_status_display(),
            'images_url': request.build_absolute_uri(self.images.url),
            'active': self.active,
            'service_name': self.order.get_service_name_display(),
            'created_at': self.created_at.strftime(FORMAT_DATE),
            'modified_at': self.modified_at.strftime(FORMAT_DATE),
            'analysis_name': self.analysis_name,
            'report': '',
            'message_to_user': '',
        }

        if self.report.name:
            dict_['report'] = request.build_absolute_uri(self.report.url)

        if self.status == self.Status.INVALID_INFOS:
            dict_['message_to_user'] = self.message_to_user

        return dict_


class DosimetryAnalysisBase(AnalysisBase):

    injected_activity = models.FloatField('Injected Activity', validators=[MinValueValidator(0.0)])
    administration_datetime = models.DateTimeField('Administration Datetime')

    class Meta:
        abstract = True

    def to_dict(self, request):

        dict_ = super().to_dict(request)

        dict_['calibration_id'] = self.calibration.uuid
        dict_['injected_activity'] = self.injected_activity
        dict_['administration_datetime'] = self.administration_datetime.strftime(FORMAT_DATE)

        return dict_

    def _generate_code(self):
        clinic_id = self.order.user.pk
        year = str(self.created_at.year)[2:]
        isotope = self.calibration.isotope
        order_id = self.order.pk
        id = self.pk
        code = self.CODE
        return f'{clinic_id:04}.{order_id:04}.{isotope}.{year}/{id:04}-{code}'


class ClinicDosimetryAnalysis(DosimetryAnalysisBase):

    SERVICE_NAME_CODE = Order.ServicesName.CLINIC_DOSIMETRY.value
    CODE = Order.SERVICES_CODES[SERVICE_NAME_CODE]

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
        ordering = ['-created_at']


class PreClinicDosimetryAnalysis(DosimetryAnalysisBase):

    SERVICE_NAME_CODE = Order.ServicesName.PRECLINIC_DOSIMETRY.value
    CODE = Order.SERVICES_CODES[SERVICE_NAME_CODE]

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
        ordering = ['-created_at']


class SegmentationAnalysis(AnalysisBase):

    SERVICE_NAME_CODE = Order.ServicesName.SEGMENTANTION_QUANTIFICATION.value
    CODE = Order.SERVICES_CODES[SERVICE_NAME_CODE]

    # TODO: Talvez esse relacionamento pode ficar na classe Abstrata
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='segmentation_analysis')

    images = models.FileField('Images', upload_to=upload_segmentation_analysis_to)

    class Meta:
        db_table = 'segmentation_analysis'
        verbose_name = 'Segmentation Analysis'
        verbose_name_plural = 'Segmentation Analyzes'
        unique_together = (
            'order',
            'analysis_name',
        )
        ordering = ['-created_at']

    def _generate_code(self):
        clinic_id = self.order.user.pk
        year = str(self.created_at.year)[2:]
        order_id = self.order.pk
        id = self.pk
        code = self.CODE
        return f'{clinic_id:04}.{order_id:04}.{year}/{id:04}-{code}'

    def to_dict(self, request):

        dict_ = super().to_dict(request)

        return dict_


class RadiosynoAnalysis(AnalysisBase):

    SERVICE_NAME_CODE = Order.ServicesName.RADIOSYNOVIORTHESIS.value
    CODE = Order.SERVICES_CODES[SERVICE_NAME_CODE]

    isotope = models.ForeignKey('Isotope', on_delete=models.CASCADE, related_name='radiosyno_analysis')
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='radiosyno_analysis')
    images = models.FileField('Images', upload_to=upload_radiosyno_analysis_to)

    class Meta:
        db_table = 'radiosyno_analysis'
        verbose_name = 'Radiosynoviorthesis Analysis'
        verbose_name_plural = 'Radiosynoviorthesis Analyzes'
        unique_together = (
            'order',
            'analysis_name',
        )
        ordering = ['-created_at']

    def to_dict(self, request):

        dict_ = super().to_dict(request)

        dict_['isotope'] = self.isotope.name

        return dict_

    def _generate_code(self):
        clinic_id = self.order.user.pk
        year = str(self.created_at.year)[2:]
        isotope = self.isotope
        order_id = self.order.pk
        id = self.pk
        code = self.CODE
        return f'{clinic_id:04}.{order_id:04}.{isotope}.{year}/{id:04}-{code}'
