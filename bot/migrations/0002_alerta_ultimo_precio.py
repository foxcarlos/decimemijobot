# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-29 21:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='alerta',
            name='ultimo_precio',
            field=models.FloatField(default=0.0),
        ),
    ]
