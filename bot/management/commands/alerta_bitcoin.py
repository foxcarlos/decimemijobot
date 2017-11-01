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

    def obtener_precio(self, comando):
        if comando == 'bitcoin':
            ultimo_precio = self.obtener_precio_bitcoin()
        elif comando == 'dolartoday':
            ultimo_precio = self.obtener_precio_dolar_paralelo_venezuela()
        else:
            ultimo_precio = 0
        return ultimo_precio

    def generar_alerta(self, comando):
        precio_actual = self.obtener_precio(comando)

        lista_de_alertas = AlertaUsuario.objects.filter(
                alerta__comando=comando, estado="A").exclude(
                        alerta__ultimo_precio=precio_actual)

        ultimo_precio = lista_de_alertas[0].alerta.ultimo_precio\
                if lista_de_alertas else 0

        if precio_actual > ultimo_precio:
            alta_o_baja = "Subio"
        elif precio_actual < ultimo_precio:
            alta_o_baja = "bajo"
        else:
            alta_o_baja = "Se mantuvo"

        for chat in lista_de_alertas:
            mensaje_a_chat = "El precio del {0} {1} a: {2}".format(
                    comando,
                    alta_o_baja,
                    precio_actual)

            DjangoTelegramBot.dispatcher.bot.sendMessage(
                    chat.chat_id,
                    mensaje_a_chat)

        Alerta.objects.filter(comando=comando).update(
                ultimo_precio=precio_actual)


    def handle(self, *args, **options):

        if 'dolartoday' in options.get("comando"):
            self.generar_alerta('dolartoday')
        elif 'bitcoin' in options.get("comando"):
            self.generar_alerta("bitcoin")

        self.stdout.write('Ejecutando comando')
