import os
from decimal import Decimal
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from web_server.core.models import CreationModificationBase


# TODO: Codigo repetido
def _timestamp(datetime):
    return datetime.strftime('%d%m%y%H%M%S')


def upload_to(instance, filename):

    datetime_now = now()
    time = _timestamp(datetime_now)

    _, extension = os.path.splitext(filename)

    id = instance.user.pk
    prefix = f'{id}/signatures/{slugify(instance.plan)}'

    filename = f'bill_{time}{extension}'

    return f'{prefix}/{filename}'


class Benefit(CreationModificationBase):

    uuid = models.UUIDField(default=uuid4, editable=False, unique=True)
    name = models.CharField(max_length=160, unique=True)
    uri = models.CharField(max_length=160)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Benefit')
        verbose_name_plural = _('Benefits')
        ordering = ['created_at']


class Signature(CreationModificationBase):
    class Modality(models.TextChoices):
        MONTHLY = ('M', 'monthly')
        YEARLY = ('Y', 'yearly')

    uuid = models.UUIDField(default=uuid4, editable=False, unique=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='signatures')
    plan = models.CharField(max_length=160)
    modality = models.CharField('Modality', max_length=2, choices=Modality.choices, default=Modality.YEARLY)
    discount = models.DecimalField('Discount', max_digits=14, decimal_places=2, default=Decimal('0.00'))
    price = models.DecimalField('Price', max_digits=14, decimal_places=2)
    benefits = models.ManyToManyField(Benefit, related_name='signatures', through='SignatureBenefit')

    hired_period_initial = models.DateField(null=True, blank=True)
    hired_period_end = models.DateField(null=True, blank=True)
    test_period_initial = models.DateField(null=True, blank=True)
    test_period_end = models.DateField(null=True, blank=True)

    activated = models.BooleanField(default=False)

    bill = models.FileField('Bill', upload_to=upload_to, blank=True, null=True)

    class Meta:
        verbose_name = _('Signature')
        verbose_name_plural = _('Signatures')
        ordering = ('created_at',)
        unique_together = ('user', 'plan')

    def __str__(self):
        return self.plan

    def clean(self):

        if (self.hired_period_initial and self.hired_period_end) and (
            self.hired_period_initial > self.hired_period_end
        ):
            raise ValidationError({'hired_period_end': _('The start date must be after the end date.')})

        if (self.test_period_initial and self.test_period_end) and (self.test_period_initial > self.test_period_end):
            raise ValidationError({'test_period_end': _('The start date must be after the end date.')})

    @property
    def hired_period(self):
        if self.hired_period_initial and self.hired_period_end:
            return {'initial': self.hired_period_initial, 'end': self.hired_period_end}
        return None

    @property
    def test_period(self):
        if self.test_period_initial and self.test_period_end:
            return {'initial': self.test_period_initial, 'end': self.test_period_end}
        return None


class SignatureBenefit(models.Model):

    benefit = models.ForeignKey(Benefit, on_delete=models.CASCADE)
    signature = models.ForeignKey(Signature, on_delete=models.CASCADE)

    created_at = models.DateTimeField(_('Creation Date and Time'), auto_now_add=True)

    class Meta:
        unique_together = (('benefit', 'signature'),)
        ordering = ('signature', 'benefit')
