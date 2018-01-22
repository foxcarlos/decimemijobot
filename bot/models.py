#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from datetime import timedelta, datetime

# Create your models here.

class User(models.Model):
    '''.'''

    chat_id = models.IntegerField(default=0)
    username = models.CharField(max_length=50, blank=True, null=True,)
    first_name = models.CharField(max_length=50, blank=True, null=True,)
    last_name = models.CharField(max_length=50, blank=True, null=True,)
    language_code = models.CharField(max_length=50, blank=True, null=True,)

    def __str__(self):
        return u'{0}'.format(self.username)

    class Meta:
        '''.'''
        verbose_name_plural = 'Users'
        verbose_name = 'User'
        ordering = ['username']

class Grupo(models.Model):
    grupo_id = models.IntegerField(default=0)
    descripcion = models.CharField(max_length=200, blank=True, null=True)
    tipo = models.CharField(max_length=50, blank=True, null=True)


class Comando(models.Model):
    nombre = models.CharField(max_length=100, blank=False, null=False)
    descripcion = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.nombre


class ComandoEstado(models.Model):
    grupo_id = models.IntegerField(default=0)
    comando = models.ForeignKey(Comando, related_name='Comandos', on_delete=models.CASCADE)
    activo = models.BooleanField(default=True)
    chat_id = models.IntegerField(default=0)


class Alerta(models.Model):
    '''.'''
    comando = models.CharField(max_length=100, blank=True, null=True, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=False)

    def __str__(self):
        return self.comando

    class Meta:
        '''.'''
        verbose_name_plural = 'Alertas'
        verbose_name = 'Alerta'
        ordering = ['comando']


class AlertaUsuario(models.Model):
    '''.'''
    alerta = models.ForeignKey(Alerta, related_name='alertas', on_delete=models.CASCADE)
    estado = models.CharField(max_length=3, default="I",\
            choices=(
                ('A', 'On'),
                ('I', 'Off')
                ),)

    chat_id = models.IntegerField(blank=True, null=False)
    chat_username = models.CharField(max_length=100, blank=True, null=True)
    frecuencia = models.IntegerField(default=120,
            verbose_name="frecuencia de notificacion de alertas en minutos",
            help_text="Tiempo en segundos")
    porcentaje_cambio = models.IntegerField(default=0,
            verbose_name="Porcentaje de cambio en la tasa",
            help_text="Numero entero")
    ultima_actualizacion = models.DateTimeField(default=datetime.now(), blank=True, null=True)
    ultimo_precio = models.FloatField(default=0.0)

    def __str__(self):
        return self.alerta.comando

    class Meta:
        '''.'''
        verbose_name_plural = 'AlertasUsuarios'
        verbose_name = 'AlertaUsuario'
        ordering = ['alerta']


