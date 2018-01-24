# Generated by Django 2.0.1 on 2018-01-24 13:27

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0026_auto_20180118_1356'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contrato',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contrato', models.IntegerField()),
                ('status', models.BooleanField(default=True)),
                ('operacion', models.CharField(blank=True, max_length=100, null=True)),
                ('fecha', models.DateTimeField(default=datetime.datetime(2018, 1, 24, 10, 27, 36, 10747))),
            ],
            options={
                'verbose_name_plural': 'Contratos',
                'ordering': ['fecha'],
                'verbose_name': 'Contrato',
            },
        ),
        migrations.CreateModel(
            name='PersonaContrato',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo_buyer_seller', models.CharField(blank=True, max_length=50, null=True)),
                ('puntuacion', models.CharField(choices=[('pos', 'Positivo'), ('neg', 'Negativo'), ('neu', 'Neutral')], default='neu', max_length=15)),
                ('comentario', models.CharField(blank=True, max_length=100, null=True)),
                ('contrato', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contratos', to='bot.Contrato')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='users', to='bot.User')),
            ],
        ),
        migrations.AlterModelOptions(
            name='grupo',
            options={'ordering': ['descripcion'], 'verbose_name': 'Grupo', 'verbose_name_plural': 'Grupos'},
        ),
        migrations.AlterField(
            model_name='alertausuario',
            name='ultima_actualizacion',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2018, 1, 24, 10, 27, 36, 10189), null=True),
        ),
        migrations.AddField(
            model_name='contrato',
            name='grupo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bot.Grupo'),
        ),
    ]
