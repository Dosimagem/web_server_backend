# Generated by Django 4.1 on 2022-09-05 03:38

from django.db import migrations, models
import functools
import web_server.service.models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0006_alter_calibration_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='calibration',
            name='images',
            field=models.FileField(null=True, upload_to=functools.partial(web_server.service.models.upload_to, *(), **{'type': 'calibrations'}), verbose_name='Calibration Images'),
        ),
    ]
