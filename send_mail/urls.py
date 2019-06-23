from django.conf.urls import include, url
from django.contrib import admin

from .views import Login, Logout, Registro, Calculo, DatosPersonales

urlpatterns = [
    # #url(r'^trabajo/(?P<productor_id>\d+)/', CrearImpresion.as_view(), name='crear_trabajo'),
    #url(r'^trabajo/', CrearImpresion.as_view()),
    url(r'^login/$', Login.as_view(), name='login'),
    url(r'^logout/$', Logout.as_view(), name='logout'),
    url(r'^registro/$', Registro.as_view(), name='registro'),
    url(r'^calculo/$', Calculo.as_view(), name='calculo'),
    url(r'^datosp/$', DatosPersonales.as_view(), name='datospersonales'),
]