# Generated by Django 4.1 on 2022-09-20 17:30

from django.db import migrations, models
import functools
import web_server.service.models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0004_alter_clinicdosimetryanalysis_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='calibration',
            name='images',
            field=models.FileField(upload_to=functools.partial(web_server.service.models.upload_to, *(), **{'type': 'calibration'}), verbose_name='Calibration Images'),
        ),
        migrations.AlterField(
            model_name='clinicdosimetryanalysis',
            name='images',
            field=models.FileField(upload_to=functools.partial(web_server.service.models.upload_to, *(), **{'type': 'clinic_dosimetry'}), verbose_name='Images'),
        ),
        migrations.AlterField(
            model_name='clinicdosimetryanalysis',
            name='report',
            field=models.FileField(blank=True, null=True, upload_to=functools.partial(web_server.service.models.upload_to, *(), **{'type': 'report'}), verbose_name='Report'),
        ),
        migrations.AlterField(
            model_name='preclinicdosimetryanalysis',
            name='images',
            field=models.FileField(upload_to=functools.partial(web_server.service.models.upload_to, *(), **{'type': 'preclinic_dosimetry'}), verbose_name='Images'),
        ),
        migrations.AlterField(
            model_name='preclinicdosimetryanalysis',
            name='report',
            field=models.FileField(blank=True, null=True, upload_to=functools.partial(web_server.service.models.upload_to, *(), **{'type': 'report'}), verbose_name='Report'),
        ),
    ]
