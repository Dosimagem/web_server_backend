from functools import partial
import os

from django.db import models
from django.utils.timezone import now


def _normalize_email(email):
    return email.replace('@', '_').replace('.', '_')


def upload_to(instance, filename, type):

    datetime_now = now()
    time = f'{datetime_now:%H%M%S}'
    date = f'{datetime_now:%Y/%m/%d}'
    _, extension = os.path.splitext(filename)

    if type == 'img':
        user = _normalize_email(instance.requester.email)
        type = 'images'
        filename = f'images_{time}{extension}'

    if type == 'report':
        user = _normalize_email(instance.requester.email)
        type = 'report'
        filename = f'report_{time}{extension}'

    return f'{user}/{type}/{date}/{filename}'


upload_img_to = partial(upload_to, type='img')
upload_report_to = partial(upload_to, type='report')


class Service(models.Model):

    name = models.CharField('name', max_length=60)
    description = models.TextField('description', max_length=2048)
    unit_price = models.DecimalField('unit price', max_digits=14, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class BaseAbstractOrder(models.Model):

    AWAITING_PAYMENT = 'APG'
    AWAITTING_PROCESSING = 'APR'
    PROCESSING = 'PRC'
    CONCLUDED = 'CON'

    STATUS = (
        (AWAITING_PAYMENT, 'Aguardando pagamento'),
        (AWAITTING_PROCESSING, 'Aguardando processamento'),
        (PROCESSING, 'Processando'),
        (CONCLUDED, 'Concluído'),
    )

    def save(self, *args, **kwargs):
        if not self.total_price:
            self.total_price = self.service.unit_price * self.amount
        super().save(*args, **kwargs)

    requester = models.ForeignKey('core.CostumUser', on_delete=models.CASCADE)
    service = models.ForeignKey('Service', on_delete=models.CASCADE)
    amount = models.IntegerField('Amount')

    status = models.CharField('status', max_length=3, choices=STATUS)

    # this field is automatically filled in by amount and unit price of the service
    total_price = models.DecimalField('Total price', max_digits=14, decimal_places=2, null=True, blank=True)

    report = models.FileField('Report', upload_to=upload_report_to, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def get_path_report(self):
        return str(self.report)


class DosimetryOrder(BaseAbstractOrder):

    CLINICAL = 'C'
    PRECLINICAL = 'P'

    TYPES = (
        (CLINICAL, 'Clinical'),
        (PRECLINICAL, 'Pre Clinical'),
    )

    # this field is automatically filled in by service name
    type = models.CharField('Dosimetry Type', max_length=1, choices=TYPES, blank=True)
    camera_factor = models.FloatField('Camera Factor')
    radionuclide = models.CharField('Radionuclide', max_length=6)
    injected_activity = models.FloatField('Injected Activity')
    injection_datetime = models.DateTimeField('Injection datetime')
    images = models.FileField('Images', upload_to=upload_img_to)

    def save(self, *args, **kwargs):
        if not self.type:
            if 'preclinica' in self.service.name.lower():
                self.type = self.PRECLINICAL
            else:
                self.type = self.CLINICAL

        super().save(*args, **kwargs)

    def __str__(self):
        msg = ''
        if self.type == self.CLINICAL:
            msg = f'Clinical Dosimetry (id={self.pk})'
        elif self.type == self.PRECLINICAL:
            msg = f'Preclinical Dosimetry (id={self.pk})'

        return msg


class SegmentationOrder(BaseAbstractOrder):
    images = models.FileField('Images', upload_to=upload_img_to)
    observations = models.TextField('Obeservations', max_length=5000)

    def __str__(self):
        return f'Segmentantion (id={self.pk})'


class ComputationalModelOrder(BaseAbstractOrder):

    CT = 'C'
    SPECT = 'S'

    OPTIONS = (
        (CT, 'CT'),
        (SPECT, 'SPECT'),
    )

    images = models.FileField('Images', upload_to=upload_img_to)
    equipment_specification = models.CharField('Equipment Specification', max_length=1, choices=OPTIONS)

    def __str__(self):
        return f'Computational Modeling (id={self.pk})'
