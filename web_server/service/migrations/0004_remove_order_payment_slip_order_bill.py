# Generated by Django 4.1.6 on 2023-02-17 03:12

import functools

from django.db import migrations, models

import web_server.service.models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0003_alter_isotope_options_alter_isotoperadiosyno_options_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='payment_slip',
        ),
        migrations.AddField(
            model_name='order',
            name='bill',
            field=models.FileField(
                blank=True,
                null=True,
                upload_to=functools.partial(web_server.service.models.upload_to, *(), **{'type': 'payment_slip'}),
                verbose_name='Bill',
            ),
        ),
    ]
