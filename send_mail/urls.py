from django.conf.urls import include, url
from django.contrib import admin

from .views import Calculo

urlpatterns = [
    # #url(r'^trabajo/(?P<productor_id>\d+)/', CrearImpresion.as_view(), name='crear_trabajo'),
    #url(r'^trabajo/', CrearImpresion.as_view()),
    # url(r'^sendmail/$', SendMail.as_view(), name='sendmail'),
    url(r'^calculo/$', Calculo.as_view(), name='calculo'),
]
