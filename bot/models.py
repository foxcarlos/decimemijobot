from __future__ import unicode_literals

from django.db import models
from datetime import timedelta

# Create your models here.

class Alerta(models.Model):
    '''.'''
    comando = models.CharField(max_length=100, blank=True, null=True, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    ultimo_precio = models.FloatField(default=0.0)
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
    alerta = models.ForeignKey(Alerta, related_name='alertas')
    estado = models.CharField(max_length=3, default="Off",\
            choices=(
                ('A', 'On'),
                ('I', 'Off')
                ),)

    chat_id = models.IntegerField(default=0)
    chat_username = models.CharField(max_length=100, blank=True, null=True)
    frecuencia = models.IntegerField(default=1200,
            verbose_name="frecuencia de notificacion de alertas en segundos",
            help_text="Tiempo en segundos")
    porcentaje_cambio = models.IntegerField(default=0,
            verbose_name="Porcentaje de cambio en la tasa",
            help_text="Numero entero")
    ultima_actualizacion = models.DateTimeField()


    def __str__(self):
        return self.alerta.comando

    class Meta:
        '''.'''
        verbose_name_plural = 'AlertasUsuarios'
        verbose_name = 'AlertaUsuario'
        ordering = ['alerta']


