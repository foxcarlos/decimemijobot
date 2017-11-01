from django.contrib import admin

# Register your models here.
from django.contrib import admin

from .models import Alerta, AlertaUsuario

class AlertaAdmin(admin.ModelAdmin):
    model = Alerta

    list_display = ['comando', 'descripcion', 'ultimo_precio', 'activo', 'pk']
    search_fields = ['comando', 'activo']


class AlertaUsuarioAdmin(admin.ModelAdmin):
    model = AlertaUsuario

    list_display = ['alerta', 'estado', 'frecuencia', 'ultima_actualizacion',
            'chat_id', 'chat_username']
    search_fields = ['alerta', 'estado', 'chat_username']
    list_filter = ['alerta']


admin.site.register(Alerta, AlertaAdmin)
admin.site.register(AlertaUsuario, AlertaUsuarioAdmin)
