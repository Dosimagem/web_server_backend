from uuid import uuid4

from django.conf import settings
from django.db import models

from web_server.core.models import CreationModificationBase

# Create your models here.


class Notification(CreationModificationBase):
    class Kind(models.TextChoices):
        PROCESSING = ('PR', 'processing')
        ERROR = ('ER', 'error')
        SUCCESS = ('SU', 'success')

    class Meta:
        ordering = ('-created_at',)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')

    uuid = models.UUIDField(default=uuid4, editable=False, unique=True)
    checked = models.BooleanField(default=False)
    message = models.TextField()
    kind = models.CharField(max_length=2, choices=Kind.choices)

    def __str__(self):
        return self.message

    def to_dict(self):
        return {
            'id': self.uuid,
            'message': self.message,
            'checked': self.checked,
            'kind': self.get_kind_display(),
            'created_at': self.created_at,
        }

    def toogle(self):
        self.checked = not self.checked
