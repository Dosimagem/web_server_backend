from decimal import Decimal
import os

from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils.timezone import now


def _normalize_email(email):
    return email.replace('@','_').replace('.', '_')

def upload_to(instance, filename):

    datetime_now = now()
    time = f'{datetime_now:%H%M%S}'
    date = f'{datetime_now:%Y/%m/%d}'
    base, extension = os.path.splitext(filename)

    if isinstance(instance, Info):
        user = _normalize_email(instance.order.requester.email)
        type = 'images'
        filename = f'images_{time}{extension}'

    if isinstance(instance, Order):
        user =  _normalize_email(instance.requester.email)
        type = 'report'
        filename = f'report_{time}{extension}'

    return f'{user}/{type}/{date}/{filename}'



class Service(models.Model):

    name = models.CharField('name', max_length=60)
    description = models.TextField('description', max_length=2048)
    unit_price = models.DecimalField('unit price', max_digits=14, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Order(models.Model):

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


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if isinstance(self.amount, int) and isinstance(self.service.unit_price, Decimal):
            self.total_price = self.service.unit_price * self.amount


    requester = models.ForeignKey('core.CostumUser', on_delete=models.CASCADE)
    service = models.ForeignKey('Service', on_delete=models.CASCADE)
    amount = models.IntegerField('Amount')

    status = models.CharField('status', max_length=3, choices=STATUS)

    # this field is automatically filled in by amount and unit price of the service
    total_price = models.DecimalField('Total price', max_digits=14, decimal_places=2, null=True, blank=True)

    report = models.FileField('Report', upload_to=upload_to, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f'Order(id={self.id})'


class Info(models.Model):

    order = models.OneToOneField('Order', on_delete=models.CASCADE)

    camera_factor = models.FloatField('Camera Factor', null=True, blank=True)
    radionuclide = models.CharField('Radionuclide', max_length=6, null=True, blank=True)
    injected_activity = models.FloatField('Injected Activity', null=True, blank=True)
    injection_datetime = models.DateTimeField('Injection datetime', null=True, blank=True)
    images = models.FileField('Images', upload_to=upload_to, blank=True)
    obs = models.TextField('Obervations',max_length=2048, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Infos {self.order.service.name}'


@receiver(post_delete, sender=Info)
def post_delete_info(sender, instance, *args, **kwargs):
    if instance.order:
        instance.order.delete()
