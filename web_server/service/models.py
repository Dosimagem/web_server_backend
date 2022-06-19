from django.db import models


class Service(models.Model):

    name = models.CharField('name', max_length=60)
    description = models.TextField('description', max_length=2048)
    unit_price = models.DecimalField('unit price', max_digits=14, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
