from django.contrib import admin

# Register your models here.
from django.contrib import admin

from .models import Alerta, AlertaUsuario, User, Grupo, Comando, ComandoEstado, Contrato, PersonaContrato


class UserAdmin(admin.ModelAdmin):
    model = User

    list_display = ['chat_id', 'username', 'first_name', 'language_code', 'pk']
    search_fields = ['username', 'chat_id']

class AlertaAdmin(admin.ModelAdmin):
    model = Alerta

    list_display = ['comando', 'descripcion', 'activo', 'pk']
    search_fields = ['comando', 'activo']


class AlertaUsuarioAdmin(admin.ModelAdmin):
    model = AlertaUsuario

    list_display = ['alerta', 'estado', 'frecuencia', 'porcentaje_cambio',
            'ultima_actualizacion', 'ultimo_precio',
            'chat_id', 'chat_username']
    search_fields = ['alerta', 'estado', 'chat_username', 'chat_id']
    list_filter = ['alerta', 'estado']


class GrupoAdmin(admin.ModelAdmin):
    model = Grupo

    list_display = ['grupo_id', 'descripcion', 'tipo']
    search_fields = ['grupo_id', 'descripcion', 'tipo']
    list_filter = ['tipo']


class ComandoAdmin(admin.ModelAdmin):
    model = Comando

    list_display = ["nombre", "descripcion"]
    search_fields = ["nombre", "descripcion"]


class ComandoEstadoAdmin(admin.ModelAdmin):
    model = ComandoEstado

    list_display = ["grupo_id" , "comando", "activo", "chat_id"]
    search_fields = ["grupo_id" , "comando", "chat_id"]
    list_filter = ['activo']


class ContratoAdmin(admin.ModelAdmin):
    model = Contrato

    list_display = ["contrato" , "status", "operacion", "fecha", "grupo"]
    search_fields = ["contrato" , "status" ]
    list_filter = ['status']


class PersonaContratoAdmin(admin.ModelAdmin):
    model = PersonaContrato

    list_display = ["contrato" , "user", "tipo_buyer_seller", "puntuacion", "comentario"]
    search_fields = ["contrato" , "user"]
    list_filter = ['tipo_buyer_seller', "puntuacion"]


admin.site.register(User, UserAdmin)
admin.site.register(Alerta, AlertaAdmin)
admin.site.register(AlertaUsuario, AlertaUsuarioAdmin)
admin.site.register(Grupo, GrupoAdmin)
admin.site.register(Comando, ComandoAdmin)
admin.site.register(ComandoEstado, ComandoEstadoAdmin)
admin.site.register(Contrato, ContratoAdmin)
admin.site.register(PersonaContrato, PersonaContratoAdmin)

