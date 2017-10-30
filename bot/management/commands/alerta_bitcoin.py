from django.core.management.base import BaseCommand
from django_telegrambot.apps import DjangoTelegramBot

from bot.models import Alerta, AlertaUsuario
from django.db.models import Q

import requests


class Command(BaseCommand):
    help = "Verifica el precio actual del botcoin, si cambio envia un alerta"

    def add_arguments(self, parser):
        parser.add_argument('comando', nargs='+', type=str)

    def obtener_precio_bitcoin(self):
        url = "https://api.coinbase.com/v2/exchange-rates?currency=BTC"
        get_price = requests.get(url).json().get("data").get("rates").get("USD")
        response = float(get_price)
        return response

    def obtener_precio_dolar_paralelo_venezuela(self):
        rq = requests.get('https://s3.amazonaws.com/dolartoday/data.json')
        devuelto = rq.json()
        response = devuelto['USD']['transferencia']
        return response

    def generar_alerta_dt(self):
        pass

    def generar_alerta_btc(self):
        precio_actual_botcoin = self.obtener_precio_bitcoin()

        lista_de_alertas_bitcoin = AlertaUsuario.objects.filter(
                alerta__comando='bitcoin').exclude(
                        alerta__ultimo_precio=precio_actual_botcoin)

        ultimo_precio_bitcoin = lista_de_alertas_bitcoin[0].alerta.ultimo_precio\
                if lista_de_alertas_bitcoin else 0

        if precio_actual_botcoin > ultimo_precio_bitcoin:
            alta_o_baja = "Subio"
        elif precio_actual_botcoin < ultimo_precio_bitcoin:
            alta_o_baja = "bajo"
        else:
            alta_o_baja = "Se mantuvo"

        for chat in lista_de_alertas_bitcoin:
            mensaje_a_chat = "El precio del bitcoin {0} a: {1}".format(
                    alta_o_baja,
                    precio_actual_botcoin)

            DjangoTelegramBot.dispatcher.bot.sendMessage(
                    chat.chat_id,
                    mensaje_a_chat)

        Alerta.objects.filter(comando="bitcoin").update(
                ultimo_precio=precio_actual_botcoin)

    def handle(self, *args, **options):

        if 'dolartoday' in options.get("comando"):
            self.generar_alerta_dt()
        elif 'bitcoin' in options.get("comando"):
            self.generar_alerta_btc()

        self.stdout.write('Ejecutando comando')
