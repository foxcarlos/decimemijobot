# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-01 15:44
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0007_alertausuario_procentaje_cambio'),
    ]

    operations = [
        migrations.RenameField(
            model_name='alertausuario',
            old_name='procentaje_cambio',
            new_name='porcentaje_cambio',
        ),
    ]