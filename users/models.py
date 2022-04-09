from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone =  models.CharField(max_length=30, blank=True)
    institution =  models.CharField(max_length=30, blank=True)
    role =  models.CharField(max_length=30, blank=True)