# Generated by Django 4.1.6 on 2023-02-17 01:30

import functools

from django.db import migrations, models

import web_server.service.models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0002_isotoperadiosyno_alter_radiosynoanalysis_isotope'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='isotope',
            options={
                'ordering': ['-created_at'],
                'verbose_name': 'Isotope for dosimetry',
                'verbose_name_plural': 'Isotopes for dosimetry',
            },
        ),
        migrations.AlterModelOptions(
            name='isotoperadiosyno',
            options={
                'ordering': ['-created_at'],
                'verbose_name': 'Isotope for radiosunoviorthesis',
                'verbose_name_plural': 'Isotopes for radiosunoviorthesis',
            },
        ),
        migrations.AddField(
            model_name='order',
            name='payment_slip',
            field=models.FileField(
                blank=True,
                null=True,
                upload_to=functools.partial(web_server.service.models.upload_to, *(), **{'type': 'payment_slip'}),
                verbose_name='Payment slip',
            ),
        ),
    ]