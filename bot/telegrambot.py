# -*- coding: utf-8 -*-
# Example code for telegrambot.py module
import requests
import logging

from telegram.ext import CommandHandler, MessageHandler, Filters
from django_telegrambot.apps import DjangoTelegramBot
from django.conf import settings

logger = logging.getLogger(__name__)

from django.db.models import Count
from django.contrib.auth.models import User as UserDjango
from bot.scrapy import NoticiasPanorama
from bot.models import Alerta, AlertaUsuario, User
# from bot.task import pool_message

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.

URL_BTC_USD = settings.CRIPTO_MONEDAS.get("URL_BTC_USD")
URL_ETH_USD = settings.CRIPTO_MONEDAS.get("URL_ETH_USD")
URL_LTC_USD = settings.CRIPTO_MONEDAS.get("URL_LTC_USD")
URL_BCH_USD = settings.CRIPTO_MONEDAS.get("URL_BCH_USD")
URL_DAS_USD = settings.CRIPTO_MONEDAS.get("URL_DAS_USD")
URL_BTG_USD = settings.CRIPTO_MONEDAS.get("URL_BTG_USD")
URL_XMR_USD = settings.CRIPTO_MONEDAS.get("URL_XMR_USD")
URL_XRP_USD = settings.CRIPTO_MONEDAS.get("URL_XRP_USD")
URL_BTC_ALL_EXC = settings.CRIPTO_MONEDAS.get("URL_BTC_ALL_EXC")


def usuario_nuevo(update):
    id_user = update.message.from_user.id
    usuario = update.message.from_user.username
    nombre = update.message.from_user.first_name if \
            hasattr(update.message.from_user, "first_name") else ""
    apellido = update.message.from_user.last_name if \
            hasattr(update.message.from_user, "lasta_name") else ""
    codigo_leng = update.message.from_user.language_code if\
            hasattr(update.message.from_user, "language_code") else ""

    try:
        User.objects.update_or_create(
            chat_id=id_user,
            username=usuario,
            first_name=nombre,
            last_name=apellido,
            language_code=codigo_leng
            )
    except Exception as E:
        print(E)
    return True


def get_price(url):
    return requests.get(url).json().get("data").get("rates").get("USD")


def get_price_coinmarketcap(url):
    return requests.get(url).json()[0].get("price_usd")


def all_coins(bot, update):
    bot.sendMessage(update.message.chat_id, text="Consultando... En un momento te muestro la informacion...!")
    btc = get_price(URL_BTC_USD)
    eth = get_price(URL_ETH_USD)
    ltc = get_price(URL_LTC_USD)
    bcc = get_price_coinmarketcap(URL_BCH_USD)
    das = get_price_coinmarketcap(URL_DAS_USD)
    btg = get_price_coinmarketcap(URL_BTG_USD)
    xmr = get_price_coinmarketcap(URL_XMR_USD)
    xrp = get_price_coinmarketcap(URL_XRP_USD)

    response = """Cripto Monedas hoy:\n\n\
            BTC={0:0,.2f}\n\
            ETH={1:0,.2f}\n\
            LTC={2:0,.2f}\n\
            BTCASH={3:0,.2f}\n\
            DASH={4:0,.2f}\n\
            BTGOLD={5:0,.2f}\n\
            RIPPLE={6:0,.2f}\n\
            MONERO={7:0,.2f}""".format(
                    float(btc),
                    float(eth),
                    float(ltc),
                    float(bcc),
                    float(das),
                    float(btg),
                    float(xrp),
                    float(xmr)
                    )

    bot.sendMessage(update.message.chat_id, text=response)
    usuario_nuevo(update)


def all_exchange(bot, update):
    bot.sendMessage(update.message.chat_id, text="Consultando... En un momento te muestro la informacion en USD...!")
    exchanges_btc = requests.get(URL_BTC_ALL_EXC).json().get("Data").\
            get("Exchanges")

    exchanges = ['coinbase', 'bitfinex', 'localbitcoins',
            'bitTrex', 'poloniex', 'bitstamp', 'kraken']
    response = ""

    for exchange in exchanges_btc:
        moneda = exchange.get('TOSYMBOL')
        market = exchange.get('MARKET')
        precio = exchange.get('PRICE')
        h24h = exchange.get('HIGH24HOUR')
        h24l = exchange.get('LOW24HOUR')
        open24h = exchange.get('OPEN24HOUR')
        volumen = exchange.get('VOLUME24HOUR')

        if market.lower() in exchanges:
            response += """\n
                    \u2b50\Market:{1}\n\
                    Precio:{2:0,.2f}\n\
                    24h H:{3:0,.2f}\n\
                    24h L:{4:0,.2f}\n\
                    Volum:{6:0,.2f}
                    """.format(
                            moneda,
                            market,
                            float(precio),
                            float(h24h),
                            float(h24l),
                            float(open24h),
                            float(volumen))

    bot.sendMessage(update.message.chat_id, text=response)
    usuario_nuevo(update)


def autor(bot, update):
    url = "https://gitlab.com/foxcarlos"
    response = """
    Realizado por:

    {0}""".format(url)
    bot.sendMessage(update.message.chat_id, text=response)


def bitcoin(bot, update):
    # print(update.message)
    user_first_name = update.message.from_user.first_name

    btc = get_price(URL_BTC_USD)
    response = '{0} El precio del Bitcoin es: {1:0,.2f} USD'.\
            format(user_first_name, float(btc))
    bot.sendMessage(update.message.chat_id, text=response)
    usuario_nuevo(update)


def bitcoin_satoshitango(bot, update):
    # Por peticion de Yanina y Thainelly
    user_first_name = update.message.from_user.first_name
    url = "https://api.satoshitango.com/v2/ticker"
    get_price_venta = requests.get(url).json().get("data").get("venta").\
            get("arsbtc")
    get_price_compra = requests.get(url).json().get("data").get("compra").\
            get("arsbtc")
    response = '{0} El precio del Bitcoin en SatoshiTango es: \
            {1:0,.2f} ARG para la Compra y {2:0,.2f} ARG para la Venta'.\
            format(
                    user_first_name,
                    float(get_price_compra),
                    float(get_price_venta))

    bot.sendMessage(update.message.chat_id, text=response)
    usuario_nuevo(update)


def ethereum(bot, update):
    # print(update.message)
    user_first_name = update.message.from_user.first_name
    eth = get_price(URL_ETH_USD)
    response = '{0} El precio del Ethereum es: {1:0,.2f} USD'.\
            format(user_first_name, float(eth))
    bot.sendMessage(update.message.chat_id, text=response)
    usuario_nuevo(update)


def evaluar(palabra):
    response = ""
    if '[' and ']' in palabra:
        try:
            response = str(eval(palabra.replace("[", "").replace("]", ""))) + " "
        except Exception as inst:
            response = 'Paso algo..! ,aqui esta el error {0} \
                    deja de invertar hace algo mas facil'.format(inst)
    else:
        response = palabra
    return response


def calcular(bot, update):
    print(update.message)
    parameters = update.message.text
    user_first_name = update.message.from_user.first_name
    cadena_sin_el_comando = ' '.join(parameters.split()[1:])
    cadena = ""
    response = ""

    cadena = ' '.join([evaluar(palabra) for palabra in cadena_sin_el_comando.split()])
    if not cadena:
        cadena = 'Tienes que indicar un calculo entre [ ] Ej: /calcular [2+2]'

    response = '{0} Dice: {1} '.format(user_first_name, cadena)

    bot.sendMessage(update.message.chat_id, text=response)
    usuario_nuevo(update)


def chat(bot, update):
    print(update.message)
    bot.sendMessage(update.message.chat_id,
            text='This chat information:\n {}'.format(update.effective_chat))


def dolartoday(bot, update):
    print(update.message)
    user_first_name = update.message.from_user.first_name
    rq = requests.get('https://s3.amazonaws.com/dolartoday/data.json')
    devuelto = rq.json()
    msg_response = devuelto['USD']['transferencia']

    response = '{0} El precio del paralelo en Vzla es: {1:0,.2f}'
    bot.sendMessage(update.message.chat_id, response.format(user_first_name,
        float(msg_response)))
    usuario_nuevo(update)


def echo(bot, update):
    print(update.message)
    update.message.reply_text(update.message.text)


"""
def enviar_mensajes_todos(bot, update):
    print(update.message)
    parameters = update.message.text
    cadena_sin_el_comando = ' '.join(parameters.split()[1:])

    if valida_root(update):
        users = User.objects.values('chat_id').annotate(dcount=Count('chat_id'))
        pool_message.delay(users, cadena_sin_el_comando)
"""


def error(bot, update, error):
    print(error)
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def forwarded(bot, update):
    print(update.message)
    bot.sendMessage(update.message.chat_id,
            text='This msg forwaded information:\n {}'.\
                    format(update.effective_message))


def help(bot, update):
    msg_response = """
    Lista de Comandos:

    /allcoins - Precios de bitcoin, ethereum, litecoin
    /bitcoin
    /calcular  La suma de 2 mas 2 es [2+2] y 3 por 3 es [3*3]
    /dolartoday
    /ethereum - Precio actual del Ethereum
    /litecoin - Precio actual del LiteCoin
    /set_alarma_bitcoin - Configura alertas para esta criptomoneda
    /set_alarma_ethereum - Configura alertas para esta criptomoneda
    /set_alarma_litecoin - Configura alertas para esta criptomoneda
    /help
    /panorama
    """
    user_first_name = update.message.from_user.first_name
    response = 'Ey..! {0} aqui tiene la ayuda, {1}'.format(user_first_name,
            msg_response)

    bot.sendMessage(update.message.chat_id, text=response)


def litecoin(bot, update):
    # print(update.message)
    user_first_name = update.message.from_user.first_name
    ltc = get_price(URL_LTC_USD)
    response = '{0} El precio del LiteCoin es: {1:0,.2f} USD'.\
            format(user_first_name, float(ltc))
    bot.sendMessage(update.message.chat_id, text=response)
    usuario_nuevo(update)


def me(bot, update):
    print(update.message)
    bot.sendMessage(update.message.chat_id,
            text='Tu informacion:\n{}'.format(update.effective_user))


def panorama_sucesos(bot, update):
    print(update.message)
    bot.sendMessage(update.message.chat_id, text="En un momento te muestro la informacion...!")
    noti = NoticiasPanorama()
    response = noti.sucesos()

    bot.sendMessage(update.message.chat_id, text=response)


def porno(bot, update):
    response = "Uhmmm! no se que intentas buscar, googlealo mejor"
    bot.sendMessage(update.message.chat_id, text=response)


def set_alarma_dolartoday(bot, update):
    set_alarma(bot, update, "dolartoday")


def set_alarma_bitcoin(bot, update):
    set_alarma(bot, update, "bitcoin")


def set_alarma_ethereum(bot, update):
    set_alarma(bot, update, "ethereum")


def set_alarma_litecoin(bot, update):
    set_alarma(bot, update, "litecoin")


def set_alarma(bot, update, alerta):
    response = ""
    parameters = update.message.text
    username = update.message.from_user.username
    chat_id = update.message.from_user.id
    cadena_sin_el_comando = ' '.join(parameters.split()[1:])
    obj_alerta = Alerta.objects.get(comando__icontains=alerta)
    buscar_o_crear = AlertaUsuario.objects.get_or_create(
            alerta=obj_alerta, chat_id=chat_id)[0]

    if cadena_sin_el_comando == "?":
        response = """
        Tu configuracion actual es:

        Estado:{0}
        Frecuencia en minutos:{1}
        Porcentaje de subida o bajada:{2}

        Si quieres mas ayuda escribe /set_alarma_bitcoin sin parametros

        """.format('ON' if buscar_o_crear.estado == "A" else 'OFF',
                buscar_o_crear.frecuencia,
                buscar_o_crear.porcentaje_cambio)

    elif cadena_sin_el_comando.upper() == 'ON':
        buscar_o_crear.estado = 'A'
        buscar_o_crear.chat_username = username
        buscar_o_crear.save()
        response = "Alarma activada {}".format(cadena_sin_el_comando.upper())

    elif cadena_sin_el_comando.upper() == 'OFF':
        buscar_o_crear.estado = 'I'
        buscar_o_crear.chat_username = username
        buscar_o_crear.save()
        response = "Alarma desactivada {}".format(cadena_sin_el_comando.upper())

    elif len(cadena_sin_el_comando.upper().split("MIN")) >= 2:
        minutos = cadena_sin_el_comando.upper().split("MIN")[0]
        if minutos:
            buscar_o_crear.frecuencia = minutos
            buscar_o_crear.save()
            response = "Notificacion de Alarma cambiada a cada {} minutos".\
                    format(minutos)
        else:
            response = "El comando es xxMin Ejemplo: 60min"

    elif len(cadena_sin_el_comando.upper().split("%")) >= 2:
        cantidad_porcentaje = cadena_sin_el_comando.upper().split("%")[0]
        if cantidad_porcentaje:
            buscar_o_crear.porcentaje_cambio = cantidad_porcentaje
            buscar_o_crear.save()
            response = "Alarma se enviara cuando el precio sea mayor o menor a {}%".\
                    format(cantidad_porcentaje)
        else:
            response = "El Comando es xx% , Ejemplo 5%"
    else:
        response = """
        Te doy una mano con eso:

        - Las Alarmas son:

            - set_alarma_bitcoin
            - set_alarma_dolartoday
            - set_alarma_ethereum
            - set_alarma_litecoin

        Ejemplo para modo de uso:

        - para ver tu configuracion actual:
            /set_alarma_bitcoin ?

        - Para activar o desactivar la alarma:
            /set_alarma_bitcoin on
            /set_alarma_bitcoin off

        - Para que la alarma te envie notificacion cada ciertos minutos:
            /set_alarma_bitcoin 30min

        - Para que te envie una notificacion cuando el precio suba o baje un determinado porcentaje:
            /set_alarma_bitcoin  5%

        Nota: Una buena opcion podria ser activar ambas condiciones, te envie un mensaje siempre y cuando se cumplan cualquiera de las 2 opciones, es decir cuando pasen algunos minutos u horas o el precio suba o baje, en este caso podrias  hacer lo siguiente:
            /set_alarma_bitcoin 30min
            /set_alarma_bitcoin 2%
        """

    bot.sendMessage(update.message.chat_id, text=response)


def start(bot, update):
    # print(update.message)
    bot.sendMessage(update.message.chat_id,
            text='Que fue mijo como estais!, Soy el BOT Maracucho,\
            /help pa que veais lo que puedo hacer')
    usuario_nuevo(update)


def startgroup(bot, update):
    print(update.message)
    bot.sendMessage(update.message.chat_id,
            text='Que fue mijos como estan! ,\
            /help para que vean lo que puedo hacer')
    usuario_nuevo(update)


def valida_root(update):
    print(update.message)
    root = UserDjango.objects.filter(username__icontains="foxcarlos")
    me_id = update.message.chat_id

    if root[0] and root[0].first_name == str(me_id):
        return True


def main():
    logger.info("Loading handlers for telegram bot")

    # Default dispatcher (this is related to the first bot in settings.TELEGRAM_BOT_TOKENS)
    dp = DjangoTelegramBot.dispatcher
    # To get Dispatcher related to a specific bot
    # dp = DjangoTelegramBot.getDispatcher('BOT_n_token')     #get by bot token
    # dp = DjangoTelegramBot.getDispatcher('BOT_n_username')  #get by bot username

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))

    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("ayuda", help))
    dp.add_handler(CommandHandler("?", help))

    dp.add_handler(CommandHandler("allcoins", all_coins))
    dp.add_handler(CommandHandler("price", all_exchange))
    dp.add_handler(CommandHandler("litecoin", litecoin))
    dp.add_handler(CommandHandler("bitcoin", bitcoin))
    dp.add_handler(CommandHandler("ethereum", ethereum))
    dp.add_handler(CommandHandler("satoshitango", bitcoin_satoshitango))
    dp.add_handler(CommandHandler("set_alarma_bitcoin", set_alarma_bitcoin))
    dp.add_handler(CommandHandler("set_alarma_dolartoday", set_alarma_dolartoday))
    dp.add_handler(CommandHandler("set_alarma_ethereum", set_alarma_ethereum))
    dp.add_handler(CommandHandler("set_alarma_litecoin", set_alarma_litecoin))
    dp.add_handler(CommandHandler("calcular", calcular))
    dp.add_handler(CommandHandler("dolartoday", dolartoday))
    dp.add_handler(CommandHandler("panorama", panorama_sucesos))
    # dp.add_handler(CommandHandler("masivo", enviar_mensajes_todos))
    dp.add_handler(CommandHandler("porno", porno))
    dp.add_handler(CommandHandler("autor", autor))
    dp.add_handler(CommandHandler("startgroup", startgroup))
    dp.add_handler(CommandHandler("me", me))
    dp.add_handler(CommandHandler("chat", chat))
    dp.add_handler(MessageHandler(Filters.forwarded, forwarded))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)
