from django.core.management.base import BaseCommand

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

    def handle(self, *args, **options):

        import ipdb; ipdb.set_trace() # BREAKPOINT
        self.stdout.write('Ejecutando comando')
