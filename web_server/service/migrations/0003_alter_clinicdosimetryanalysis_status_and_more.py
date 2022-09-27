# Generated by Django 4.1 on 2022-09-27 19:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0002_alter_calibration_created_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clinicdosimetryanalysis',
            name='status',
            field=models.CharField(choices=[('AI', 'Verificando informações'), ('II', 'Informações inválidas'), ('PR', 'Processando a análise'), ('CO', 'Analise conluída')], default='AI', max_length=3, verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='preclinicdosimetryanalysis',
            name='status',
            field=models.CharField(choices=[('AI', 'Verificando informações'), ('II', 'Informações inválidas'), ('PR', 'Processando a análise'), ('CO', 'Analise conluída')], default='AI', max_length=3, verbose_name='Status'),
        ),
    ]