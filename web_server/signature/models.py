from uuid import uuid4

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

from web_server.core.models import CreationModificationBase




class Benefits(CreationModificationBase):

    uuid = models.UUIDField(default=uuid4, editable=False, unique=True)
    name = models.CharField(max_length=160, unique=True)
    uri = models.URLField()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']

class Signature(CreationModificationBase):

    uuid = models.UUIDField(default=uuid4, editable=False, unique=True)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='signatures')
    name = models.CharField(max_length=160)
    price = models.DecimalField('Price', max_digits=14, decimal_places=2)
    benefits = models.ManyToManyField(Benefits, related_name='signatures')

    hired_period_init = models.DateField(null=True, blank=True)
    hired_period_end = models.DateField(null=True, blank=True)
    test_period_init = models.DateField(null=True, blank=True)
    test_period_end = models.DateField(null=True, blank=True)

    activated = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def clean(self):

        if (self.hired_period_init and self.hired_period_end) and (self.hired_period_init > self.hired_period_end):
                raise ValidationError({'hired_period': 'The start date must be after the end date.'})

        if (self.test_period_init and self.test_period_end) and (self.test_period_init > self.test_period_end):
                raise ValidationError({'test_period': 'The start date must be after the end date.'})