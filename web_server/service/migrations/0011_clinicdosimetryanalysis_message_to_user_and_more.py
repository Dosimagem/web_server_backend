# Generated by Django 4.1.1 on 2022-10-15 03:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0010_alter_order_service_name_segmentationanalysis'),
    ]

    operations = [
        migrations.AddField(
            model_name='clinicdosimetryanalysis',
            name='message_to_user',
            field=models.TextField(default='', verbose_name='Message to user'),
        ),
        migrations.AddField(
            model_name='preclinicdosimetryanalysis',
            name='message_to_user',
            field=models.TextField(default='', verbose_name='Message to user'),
        ),
        migrations.AddField(
            model_name='segmentationanalysis',
            name='message_to_user',
            field=models.TextField(default='', verbose_name='Message to user'),
        ),
    ]