from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from django.shortcuts import render, redirect
from django.http import Http404
from django.http import HttpResponseNotFound
from django.http import HttpResponseRedirect

from django.views.generic.base import View

# Django Rest
from rest_framework.views import APIView
from rest_framework import serializers

# Models y serializer
from django.db.models import Q
from calculos.views import CalculoRapido
from django.core.exceptions import ObjectDoesNotExist
from .models import *
from exchange.models import Exchange
from perfil.serializers import DatosPersonalesSerializer

class DatosPersonales(APIView):
    '''.'''
    def get(self, request):
        instancia_paises = CalculoRapido()
        paises = instancia_paises.buscar_paises(request)

        return render(request, 'perfil_index_datosp.html', paises)
    
    def post(self, request):
        '''.'''
        import ipdb;ipdb.set_trace()
        request.data._mutable = True
        request.data['pais_residencia']= 1

        serializer = DatosPersonalesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
    def put(self, request):
        pass

    def delete(self, request):
        pass

class Calculo(View):
    '''.'''
    def get(self, request):
        '''.'''
        instancia_paises = CalculoRapido()
        paises = instancia_paises.buscar_paises(request)

        return render(request, 'principal_index_calculo.html', paises)

    def post(self, request):
        '''.'''
        recibido = request.POST
        instancia_calculo = CalculoRapido()

        ok, mensaje, bitcoin, pesos, pais_seleccionado = instancia_calculo.calculo_rapido(recibido)
        if not ok:
            return render(request, 'principal_index_calculo.html',
                      {'total_pesos': pesos,
                      'error': mensaje.get('error'),
                      'mensaje': mensaje.get('mensaje'),
                      'total_bitcoin': bitcoin,
                      'moneda': recibido.get('moneda'),
                      'default': 'Seleccione_un_Pais',
                      'enviar_a': recibido.get('enviar_a'),
                      'paises': Exchange.objects.filter(activo=True).order_by('pais__nombre')
                      })

        default = 'Pais: {0} '.format(pais_seleccionado)
        if request.user.username:
            return render(request, 'principal_index_calculo.html',
                      {'total_pesos': pesos,
                      'total_bitcoin': bitcoin,
                      'moneda': recibido.get('moneda'),
                      'default': default,
                      'enviar_a': recibido.get('enviar_a'),
                      'paises': Exchange.objects.filter(activo=True).order_by('pais__nombre')
                      })


class Login(View):
    '''.'''
    def get(self, request):
        instancia_paises = CalculoRapido()
        paises = instancia_paises.buscar_paises(request)
        return render(request, 'login.html', paises)

    def post(self, request):
        '''.'''

        usuario = request.POST.get('email')
        clave = request.POST.get('clave')

        instancia_paises = CalculoRapido()
        paises = instancia_paises.buscar_paises(request)

        buscar_usuario = authenticate(username=usuario, password=clave)
        if buscar_usuario is not None:
            login(request, buscar_usuario)
            return render(request, 'index.html', paises)
        else:
            return render(request, 'login.html',\
                    {'login': 'error', 'default': paises.get('default'),\
                    'paises': paises.get('paises'),\
                    'moneda': paises.get('moneda')})
class Logout(View):
    '''.'''
    def get(self, request):
        logout(request)
        instancia_paises = CalculoRapido()
        paises = instancia_paises.buscar_paises(request)
        return render(request, 'login.html',\
                {'default': paises.get('default'),\
                'paises': paises.get('paises'),\
                'moneda': paises.get('moneda')})

class Registro(View):
    '''.'''
    def get(self, request):
        instancia_paises = CalculoRapido()
        paises = instancia_paises.buscar_paises(request)
        return render(request, 'registro.html', paises)

    def post(self, request):
        '''.'''
        usuario = request.POST.get('email')
        clave = request.POST.get('clave')
        clave2 = request.POST.get('clave2')

        instancia_paises = CalculoRapido()
        paises = instancia_paises.buscar_paises(request)

        mensaje  = paises
        if not clave or not clave2:
            mensaje['estado'] = False
            mensaje['mensaje'] = 'Todos los campos son obligatorios'
            return render(request, 'registro.html', mensaje)

        if clave != clave2:
            mensaje['estado'] =  False
            mensaje['mensaje'] = 'Contrasenas no coinciden'
            return render(request, 'registro.html', mensaje)

        buscar_usuario = User.objects.filter(username=usuario)
        if buscar_usuario:
            mensaje['estado'] = False
            mensaje['mensaje'] = 'Usuario ya existe'
            return render(request, 'registro.html', mensaje)
        else:
            user = User.objects.create_user(usuario, usuario)
            user.save()
            mensaje['estado'] = True
            mensaje['mensaje'] = 'Felicidades... Ya puedes iniciar sesion'
            return render(request, 'registro.html', mensaje)

class SendMail(View):

    def send(self):
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        msg = MIMEMultipart()
        message = "Test de envio"
        password = "Sm4bur34u"
        msg['From'] = "info@sanmartindelosandesbureau.com.ar"
        msg['To'] = "foxcarlos@gmail.com"
        msg['Subject'] = "Test de prueba"
        msg.attach(MIMEText(message, 'plain'))
        server = smtplib.SMTP_SSL('mail.sanmartindelosandesbureau.com.ar', 465)
        server.login(msg['From'], password)
        server.sendmail(msg['From'], msg['To'], msg.as_string())
        server.quit()

