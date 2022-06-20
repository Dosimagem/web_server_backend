from decimal import Decimal

from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver


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

    # TODO: report, info

    info = models.OneToOneField('Info', on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f'Order(id={self.id})'


class Info(models.Model):

    camera_factor = models.FloatField('Camera Factor', null=True, blank=True)
    radionuclide = models.CharField('Radiocuclide', max_length=6, null=True, blank=True)
    injected_activity = models.FloatField('Injeced Activity', null=True, blank=True)
    injection_datetime = models.DateTimeField('Injection datetime', null=True, blank=True)
    images = models.FileField('Images', null=True, blank=True)
    obs = models.TextField('Obervations',max_length=2048, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Info(id={self.id})'


@receiver(post_delete, sender=Order)
def post_delete_info(sender, instance, *args, **kwargs):
    if instance.info:
        instance.info.delete()
