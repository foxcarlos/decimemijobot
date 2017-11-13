# -*- coding: utf-8 -*-
# Example code for telegrambot.py module
from telegram.ext import CommandHandler, MessageHandler, Filters
from django_telegrambot.apps import DjangoTelegramBot

import requests

import logging
logger = logging.getLogger(__name__)

from django.db.models import Count
from django.contrib.auth.models import User as UserDjango
from bot.scrapy import NoticiasPanorama
from bot.models import Alerta, AlertaUsuario, User
from time import sleep


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.

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


def autor(bot, update):
    url = "https://gitlab.com/foxcarlos"
    response = """
    Realizado por:

    {0}""".format(url)
    bot.sendMessage(update.message.chat_id, text=response)


def bitcoin(bot, update):
    # print(update.message)
    user_first_name = update.message.from_user.first_name
    url = "https://api.coinbase.com/v2/exchange-rates?currency=BTC"
    get_price = requests.get(url).json().get("data").get("rates").get("USD")
    response = '{0} El precio del Bitcoin es: {1:0,.2f} USD'.\
            format(user_first_name, float(get_price))
    bot.sendMessage(update.message.chat_id, text=response)
    usuario_nuevo(update)


def bitcoin_satoshitango(bot, update):
    # Por peticion de Yanina y Thainelly
    user_first_name = update.message.from_user.first_name
    url = "https://api.satoshitango.com/v2/ticker"
    get_price_venta = requests.get(url).json().get("data").get("venta").get("arsbtc")
    get_price_compra = requests.get(url).json().get("data").get("compra").get("arsbtc")
    response = '{0} El precio del Bitcoin en SatoshiTango es: {1:0,.2f} ARG para la Compra y {2:0,.2f} ARG para la Venta'.\
            format(user_first_name, float(get_price_compra), float(get_price_venta))
    bot.sendMessage(update.message.chat_id, text=response)
    usuario_nuevo(update)


def calcular(bot, update):
    print(update.message)
    parameters = update.message.text
    user_first_name = update.message.from_user.first_name
    cadena_sin_el_comando = ' '.join(parameters.split()[1:])
    cadena = ""
    palabra = ""
    response = ""

    try:
        # TODO: Esto se puede hacer en una linea con lista por comprension lo
        # dejo asi por ahora para que se entienda un poco mejor
        for palabra in cadena_sin_el_comando.split():
            if palabra.find("[", 0, len(palabra)) >= 0:
                cadena += str(eval(palabra.replace("[", "").replace("]", ""))) + " "
            else:
                cadena += palabra+" "

        if not cadena:
            cadena = 'Teneis que indicar un calculo entre [ ] Ej: /calcular [2+2]'

        response = '{0} Dice: {1} '.format(user_first_name, cadena)
    except Exception as inst:
        total_cal = inst
        response = 'verga paso algo..! {0}, aqui esta el error {1} deja de invertar hace algo mas facil'.format(user_first_name, total_cal)

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
    bot.sendMessage(update.message.chat_id, response.format(user_first_name, float(msg_response)))
    usuario_nuevo(update)


def echo(bot, update):
    print(update.message)
    update.message.reply_text(update.message.text)


def enviar_mensajes_todos(bot, update):
    print(update.message)
    parameters = update.message.text
    cadena_sin_el_comando = ' '.join(parameters.split()[1:])

    if valida_root(update):
        users = User.objects.values('chat_id').annotate(dcount=Count('chat_id'))
        for user in users if cadena_sin_el_comando else '':
            try:
                bot.sendMessage(user.get("chat_id"), text=cadena_sin_el_comando)
                print(user.get("chat_id ", cadena_sin_el_comando))
            except Exception as E:
                print(E)
            sleep(3)


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def forwarded(bot, update):
    print(update.message)
    bot.sendMessage(update.message.chat_id,
            text='This msg forwaded information:\n {}'.\
                    format(update.effective_message))


def help(bot, update):
    msg_response = """
    Lista de Comandos:

    /bitcoin
    /calcular  La suma de 2 mas  es [2+2] y 3 por 3 es [3*3]
    /dolartoday
    /set_alarma_bitcoin
    /help
    /panorama
    """
    user_first_name = update.message.from_user.first_name
    response = 'Ey..! {0} aqui teneis tu ayuda, {1}'.format(user_first_name, msg_response)

    bot.sendMessage(update.message.chat_id, text=response)


def me(bot, update):
    print(update.message)
    bot.sendMessage(update.message.chat_id,
            text='Tu informacion:\n{}'.format(update.effective_user))


def panorama_sucesos(bot, update):
    print(update.message)
    noti = NoticiasPanorama()
    response = noti.sucesos()

    bot.sendMessage(update.message.chat_id, text=response)


def porno(bot, update):
    response = "Uhmmm! no se que intentais buscar, googlealo mejor mijo"
    bot.sendMessage(update.message.chat_id, text=response)


def set_alarma_bitcoin(bot, update):
    response = ""
    parameters = update.message.text
    username = update.message.from_user.username
    chat_id = update.message.from_user.id
    cadena_sin_el_comando = ' '.join(parameters.split()[1:])
    bitcoin = Alerta.objects.get(comando__icontains="bitcoin")
    buscar_o_crear = AlertaUsuario.objects.get_or_create(alerta=bitcoin, chat_id=chat_id)[0]

    if cadena_sin_el_comando == "?":
        response = """
        Tu configuracion actual es:

        Estado:{0}
        Frecuencia en minutos:{1}
        Porcentaje de subida o bajada:{2}

        Si quieres mas ayuda escribe /set_alarma_bitcoin sin parametros

        """.format('ON' if buscar_o_crear.estado=="A" else 'OFF',
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
        response = "Alarma activada {}".format(cadena_sin_el_comando.upper())

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
            text='Que fue mijo como estais!, Soy el BOT Maracucho , /help pa que veais lo que puedo hacer')
    usuario_nuevo(update)


def startgroup(bot, update):
    print(update.message)
    bot.sendMessage(update.message.chat_id,
            text='Que fue mijos como estan! , /help para que vean lo que puedo hacer')
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

    dp.add_handler(CommandHandler("bitcoin", bitcoin))
    dp.add_handler(CommandHandler("satoshitango", bitcoin_satoshitango))
    dp.add_handler(CommandHandler("set_alarma_bitcoin", set_alarma_bitcoin))
    dp.add_handler(CommandHandler("calcular", calcular))
    dp.add_handler(CommandHandler("dolartoday", dolartoday))
    dp.add_handler(CommandHandler("panorama", panorama_sucesos))
    dp.add_handler(CommandHandler("masivo", enviar_mensajes_todos))
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
