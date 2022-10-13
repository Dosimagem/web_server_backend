# Generated by Django 4.1 on 2022-10-03 21:27

from django.db import migrations, models

import web_server.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_alter_userprofile_created_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='email_verified',
            field=models.BooleanField(default=False, verbose_name='email_verified'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='phone',
            field=models.CharField(
                max_length=30,
                validators=[web_server.core.validators.validate_phone],
                verbose_name='Phone',
            ),
        ),
    ]
