# -*- coding: utf-8 -*-
# Example code for telegrambot.py module
from telegram.ext import CommandHandler, MessageHandler, Filters
from django_telegrambot.apps import DjangoTelegramBot

import requests

import logging
logger = logging.getLogger(__name__)

from bot.scrapy import NoticiasPanorama
from bot.models import Alerta, AlertaUsuario


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.

def usuario_nuevo(update):

    id_user = update.message.from_user.id
    usuario = update.message.from_user.username
    nombre = update.message.from_user.first_name
    apellido = update.message.from_user.last_name
    codigo_leng = update.message.from_user.language_code

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

def start(bot, update):
    # print(update.message)
    bot.sendMessage(update.message.chat_id, text='Que fue mijo como estais!')
    usuario_nuevo(update)


def startgroup(bot, update):
    print(update.message)
    bot.sendMessage(update.message.chat_id, text='Que fue mijos como estan! , /help para que vean lo que puedo hacer')


def me(bot, update):
    print(update.message)
    bot.sendMessage(update.message.chat_id, text='Tu informacion:\n{}'.format(update.effective_user))


def chat(bot, update):
    print(update.message)
    bot.sendMessage(update.message.chat_id, text='This chat information:\n {}'.format(update.effective_chat))


def forwarded(bot, update):
    print(update.message)
    bot.sendMessage(update.message.chat_id, text='This msg forwaded information:\n {}'.format(update.effective_message))


def bitcoin(bot, update):
    print(update.message)
    user_first_name = update.message.from_user.first_name
    url = "https://api.coinbase.com/v2/exchange-rates?currency=BTC"
    get_price = requests.get(url).json().get("data").get("rates").get("USD")
    response = '{0} El precio del Bitcoin es: {1:0,.2f} USD'.format(user_first_name, float(get_price))
    bot.sendMessage(update.message.chat_id, text=response)


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


def dolartoday(bot, update):
    print(update.message)
    user_first_name = update.message.from_user.first_name
    rq = requests.get('https://s3.amazonaws.com/dolartoday/data.json')
    devuelto = rq.json()
    msg_response = devuelto['USD']['transferencia']

    response = '{0} El precio del paralelo en Vzla es: {1:0,.2f}'
    bot.sendMessage(update.message.chat_id, response.format(user_first_name, float(msg_response)))


def echo(bot, update):
    print(update.message)
    update.message.reply_text(update.message.text)


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def help(bot, update):
    msg_response = """
    Lista de Comandos:

    /bitcoin
    /calcular  La suma de 2 mas  es [2+2] y 3 por 3 es [3*3]
    /dolartoday
    /help
    /panorama
    """
    user_first_name = update.message.from_user.first_name
    response = 'Ey..! {0} aqui teneis tu ayuda, {1}'.format(user_first_name, msg_response)

    bot.sendMessage(update.message.chat_id, text=response)


def panorama_sucesos(bot, update):
    noti = NoticiasPanorama()
    response = noti.sucesos()

    bot.sendMessage(update.message.chat_id, text=response)

def porno(bot, update):
    response = "Uhmmm! no se que intentais buscar, googlealo mejor mijo"
    bot.sendMessage(update.message.chat_id, text=response)

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
    dp.add_handler(CommandHandler("calcular", calcular))
    dp.add_handler(CommandHandler("dolartoday", dolartoday))
    dp.add_handler(CommandHandler("panorama", panorama_sucesos))
    dp.add_handler(CommandHandler("porno", porno))

    dp.add_handler(CommandHandler("startgroup", startgroup))
    dp.add_handler(CommandHandler("me", me))
    dp.add_handler(CommandHandler("chat", chat))
    dp.add_handler(MessageHandler(Filters.forwarded , forwarded))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)


