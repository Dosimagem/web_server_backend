# Generated by Django 4.1 on 2022-09-24 04:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='calibration',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Creation Date and Time'),
        ),
        migrations.AlterField(
            model_name='calibration',
            name='modified_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Modificatioin Date and Time'),
        ),
        migrations.AlterField(
            model_name='clinicdosimetryanalysis',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Creation Date and Time'),
        ),
        migrations.AlterField(
            model_name='clinicdosimetryanalysis',
            name='modified_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Modificatioin Date and Time'),
        ),
        migrations.AlterField(
            model_name='isotope',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Creation Date and Time'),
        ),
        migrations.AlterField(
            model_name='isotope',
            name='modified_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Modificatioin Date and Time'),
        ),
        migrations.AlterField(
            model_name='order',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Creation Date and Time'),
        ),
        migrations.AlterField(
            model_name='order',
            name='modified_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Modificatioin Date and Time'),
        ),
        migrations.AlterField(
            model_name='preclinicdosimetryanalysis',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Creation Date and Time'),
        ),
        migrations.AlterField(
            model_name='preclinicdosimetryanalysis',
            name='modified_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Modificatioin Date and Time'),
        ),
    ]