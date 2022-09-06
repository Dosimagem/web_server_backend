# Generated by Django 4.1 on 2022-09-04 19:29

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('service', '0004_isotope'),
    ]

    operations = [
        migrations.CreateModel(
            name='Calibration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('calibration_name', models.CharField(max_length=24, verbose_name='Calibration Name')),
                ('syringe_activity', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='Syringe Activity')),
                ('residual_syringe_activity', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='Residual Syringe Activity')),
                ('measurement_datetime', models.DateTimeField(verbose_name='Measurement Datetime')),
                ('phantom_volume', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='Phantom Volume')),
                ('acquisition_time', models.TimeField(verbose_name='Acquisition Time')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('isotope', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='calibrations', to='service.isotope')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='calibrations', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]