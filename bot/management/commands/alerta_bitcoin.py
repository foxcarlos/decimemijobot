from django.core.management.base import BaseCommand
from django_telegrambot.apps import DjangoTelegramBot

from bot.models import Alerta, AlertaUsuario
from django.db.models import Q

import requests
from datetime import datetime, timedelta


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

    def validar_alarma(self, comando, chat):
        ultimo_precio = chat.ultimo_precio if chat.ultimo_precio else 0
        precio_actual = self.obtener_precio(comando)

        if precio_actual > ultimo_precio:
            alta_o_baja = "Subio"
        elif precio_actual < ultimo_precio:
            alta_o_baja = "bajo"
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
            if precio_actual >= ultimo_precio * eval("1.{}".format(porc_cambio)) or \
                    ultimo_precio <= (ultimo_precio - (ultimo_precio*porc_cambio/100)):
                paso = True

        mensaje_a_chat = "El precio del {0} {1} a: {2}".format(
                comando,
                alta_o_baja,
                precio_actual
                )

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
                DjangoTelegramBot.dispatcher.bot.sendMessage(
                        chat.chat_id,
                        mensaje_a_chat)

                # Actualizo la Fecha
                AlertaUsuario.objects.filter(id=chat.id).update(
                        ultima_actualizacion=datetime.now(),
                        ultimo_precio=precio_actual)

    def handle(self, *args, **options):

        if 'dolartoday' in options.get("comando"):
            self.generar_alerta('dolartoday')
        elif 'bitcoin' in options.get("comando"):
            self.generar_alerta("bitcoin")

        self.stdout.write('Ejecutando comando')
