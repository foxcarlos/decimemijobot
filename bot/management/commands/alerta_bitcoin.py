#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django_telegrambot.apps import DjangoTelegramBot
from django.conf import settings

from bot.models import Alerta, AlertaUsuario
from django.db.models import Q

import requests
from datetime import datetime, timedelta
from emoji import emojize


URL_BTC_USD = settings.CRIPTO_MONEDAS.get("URL_BTC_USD")
URL_ETH_USD = settings.CRIPTO_MONEDAS.get("URL_ETH_USD")
URL_LTC_USD = settings.CRIPTO_MONEDAS.get("URL_LTC_USD")
URL_BCH_USD = settings.CRIPTO_MONEDAS.get("URL_BCH_USD")
URL_DAS_USD = settings.CRIPTO_MONEDAS.get("URL_DAS_USD")
URL_BTG_USD = settings.CRIPTO_MONEDAS.get("URL_BTG_USD")
URL_XMR_USD = settings.CRIPTO_MONEDAS.get("URL_XMR_USD")
URL_XRP_USD = settings.CRIPTO_MONEDAS.get("URL_XRP_USD")
URL_PRICE_USD = settings.CRIPTO_MONEDAS.get("URL_PRICE_USD")


class Command(BaseCommand):
    help = "Verifica el precio actual del botcoin, si cambio envia un alerta"

    def add_arguments(self, parser):
        parser.add_argument('comando', nargs='+', type=str)

    def get_price(self, url):
        return requests.get(url).json().get("data").get("rates").get("USD")

    def obtener_precio_dolar_paralelo_venezuela(self):
        rq = requests.get('https://s3.amazonaws.com/dolartoday/data.json')
        devuelto = rq.json()
        response = devuelto['USD']['transferencia']
        return response

    def obtener_precio(self, comando):
        if comando == 'bitcoin':
            ultimo_precio = float(self.get_price(URL_BTC_USD))
        elif comando == 'dolartoday':
            ultimo_precio = self.obtener_precio_dolar_paralelo_venezuela()
        elif comando == 'ethereum':
            ultimo_precio = float(self.get_price(URL_ETH_USD))
        elif comando == 'litecoin':
            ultimo_precio = float(self.get_price(URL_LTC_USD))
        else:
            ultimo_precio = 0
        return ultimo_precio

    def validar_alarma(self, comando, chat):
        print(chat.id, chat)
        ultimo_precio = chat.ultimo_precio if chat.ultimo_precio else 0
        precio_actual = self.obtener_precio(comando)

        if precio_actual > ultimo_precio:
            alta_o_baja = ":arrow_up:"
        elif precio_actual < ultimo_precio:
            alta_o_baja = ":arrow_down:"
        else:
            alta_o_baja = "Se mantuvo"

        segundos_transcurridos_ultimo_aviso = datetime.now().timestamp() - \
                chat.ultima_actualizacion.timestamp()

        porc_cambio = chat.porcentaje_cambio

        paso = False
        if chat.frecuencia:
            if segundos_transcurridos_ultimo_aviso >= (chat.frecuencia * 60):
                paso = True

        if chat.porcentaje_cambio:
            if precio_actual >= (ultimo_precio + (ultimo_precio * (porc_cambio / 100))) or \
                    precio_actual <= (ultimo_precio - (ultimo_precio * (porc_cambio / 100))):
                paso = True

        preparar_mensaje = "El precio del {0} {1} a: {2:0,.2f}".format(
                comando,
                alta_o_baja,
                precio_actual
                )
        mensaje_a_chat = emojize(preparar_mensaje, use_aliases=True)

        return paso, mensaje_a_chat

    def generar_alerta(self, comando):

        precio_actual = self.obtener_precio(comando)

        lista_de_alertas = AlertaUsuario.objects.filter(
                alerta__comando=comando, estado="A").exclude(
                        ultimo_precio=precio_actual)

        for chat in lista_de_alertas:
            enviar, mensaje_a_chat = self.validar_alarma(comando, chat)
            if enviar:
                # Envio el Alerta
                try:
                    DjangoTelegramBot.dispatcher.bot.sendMessage(
                            chat.chat_id,
                            mensaje_a_chat)
                except Exception as E:
                    continue

                # Actualizo la Fecha
                AlertaUsuario.objects.filter(id=chat.id).update(
                        ultima_actualizacion=datetime.now(),
                        ultimo_precio=precio_actual)

    def handle(self, *args, **options):

        if 'dolartoday' in options.get("comando"):
            self.generar_alerta('dolartoday')
        elif 'bitcoin' in options.get("comando"):
            self.generar_alerta("bitcoin")
        elif 'ethereum' in options.get("comando"):
            self.generar_alerta("ethereum")
        elif 'litecoin' in options.get("comando"):
            self.generar_alerta("litecoin")

        self.stdout.write('Ejecutando comando')
