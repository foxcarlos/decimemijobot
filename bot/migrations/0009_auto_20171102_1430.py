# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-02 14:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0008_auto_20171101_1544'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alertausuario',
            name='estado',
            field=models.CharField(choices=[('A', 'On'), ('I', 'Off')], default='I', max_length=3),
        ),
    ]
