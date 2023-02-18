from django.db import models
from django.utils.translation import gettext_lazy as _

from web_server.core.models import CreationModificationBase


class Isotope(CreationModificationBase):

    name = models.CharField(max_length=6, unique=True)

    dosimetry = models.BooleanField(default=False)
    radiosyno = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('Isotope')
        verbose_name_plural = _('Isotopes')
        ordering = ['-created_at']

    def __str__(self):
        return self.name
