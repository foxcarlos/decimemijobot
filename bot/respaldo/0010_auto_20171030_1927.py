# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-30 19:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0009_alertausuario_periodicidad'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alertausuario',
            name='periodicidad',
            field=models.IntegerField(),
        ),
    ]
