# Generated by Django 2.0.1 on 2018-01-24 18:03

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0035_auto_20180124_1458'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alertausuario',
            name='ultima_actualizacion',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2018, 1, 24, 15, 3, 58, 317359), null=True),
        ),
        migrations.AlterField(
            model_name='contrato',
            name='fecha',
            field=models.DateTimeField(default=datetime.datetime(2018, 1, 24, 15, 3, 58, 318470)),
        ),
    ]
