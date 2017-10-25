# -*- coding: utf-8 -*-
import telebot
from telebot import types
import requests
from scrapy import NoticiasPanorama


TOKEN = '336382255:AAHwrdIgN0j3gIet0xnJfCKs78ojp1dm28s'
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['ayudame'])
def ayudame(mensaje):
    response = ayuda(mensaje)
    return True


@bot.message_handler(commands=['help'])
def help(mensaje):
    response = ayuda(mensaje)
    return True


@bot.message_handler(commands=['?'])
def signo_ayuda(mensaje):
    response = ayuda(mensaje)
    return True


@bot.message_handler(commands=['dameunaayudaitaahi'])
def dameunaayudita(mensaje):
    response = ayuda(mensaje)
    return True


def ayuda(mensaje):
    '''.'''

    chat_id = mensaje.chat.id
    msg_response = """
    Lista de Comandos:

    /bitcoin
    /calcular  La suma de 2 mas  es [2+2] y 3 por 3 es [3*3]
    /chao
    /dolartoday
    /help
    /hola
    /panorama
    /porno
    """
    user_first_name = mensaje.from_user.first_name

    response = 'Ey..! {0} aqui teneis tu ayuda, {1}'
    bot.send_message(chat_id, response.format(user_first_name, msg_response))


@bot.message_handler(commands=['bitcoin'])
def bitcoin(mensaje):
    '''.'''

    chat_id = mensaje.chat.id
    user_first_name = mensaje.from_user.first_name

    url = "https://api.coinbase.com/v2/exchange-rates?currency=BTC"
    response = requests.get(url).json().get("data").get("rates").get("USD")

    msg_response = '{0} El precio del Bitcoin es: {1:0,.2f} USD'.format(user_first_name, float(response))
    bot.send_message(chat_id, msg_response)


@bot.message_handler(commands=['calcular'])
def calculo(mensaje):
    '''.'''

    parameters = mensaje.text
    chat_id = mensaje.chat.id
    user_first_name = mensaje.from_user.first_name

    try:
        cadena_sin_el_comando = ' '.join(parameters.split()[1:])
        cadena = ""
        # TODO: Esto se puede hacer en una linea con lista por comprension lo
        # dejo asi por ahora para que se entienda un poco mejor
        for palabra in cadena_sin_el_comando.split():
            if palabra.find("[", 0, len(palabra)) >= 0:
                cadena += str(eval(palabra.replace("[", "").replace("]", ""))) + " "
            else:
                cadena += palabra+" "
            response = '{0} Dice: {1} '.format(user_first_name, cadena)
    except Exception as inst:
        total_cal = inst
        response = 'verga paso algo..! {0}, aqui esta el error {1} deja de invertar hace algo mas facil'.format(user_first_name, total_cal)

    bot.send_message(chat_id, response)


@bot.message_handler(commands=['chao'])
def chao(mensaje):
    '''.'''

    chat_id = mensaje.chat.id
    bot.send_message(chat_id, 'Dala papi nos vemos, cualquier verga gritais')


@bot.message_handler(commands=['dolartoday'])
def dolartoday(mensaje):
    '''.'''

    chat_id = mensaje.chat.id
    user_first_name = mensaje.from_user.first_name

    rq = requests.get('https://s3.amazonaws.com/dolartoday/data.json')
    devuelto = rq.json()
    msg_response = devuelto['USD']['transferencia']

    response = '{0} El precio del paralelo en Vzla es: {1:0,.2f}'
    bot.send_message(chat_id, response.format(user_first_name, float(msg_response)))


@bot.message_handler(commands=['hola'])
def comando_hola(mensaje):
    '''.'''

    print(mensaje)
    chat_id = mensaje.chat.id
    user_first_name = mensaje.from_user.first_name

    bot.send_message(chat_id, 'Que fue mijo {0} como estais..?'.format(user_first_name))


@bot.message_handler(commands=['quierocolaborar'])
def comando_quierocolaborar(mensaje):
    '''.'''

    chat_id = mensaje.chat.id
    msg_response = """
     cloname este ve: https://github.com/foxcarlos/decimemijobot
    """
    user_first_name = mensaje.from_user.first_name

    response = '{0} {1}'
    bot.send_message(chat_id, response.format(user_first_name, msg_response))


@bot.message_handler(commands=['panorama'])
def sucesos(mensaje):
    '''.'''

    chat_id = mensaje.chat.id
    noti = NoticiasPanorama()
    response = noti.sucesos()

    bot.send_message(chat_id, response)

# ---------------------------------------------------------------------------------------------
# Groserias y Jodezon


@bot.message_handler(commands=['porno'])
def porno(mensaje):
    '''.'''

    chat_id = mensaje.chat.id
    msg_response = """
     Aqui teneis  esto pervertido: https://www.redtube.com/redtube/gay
    """
    user_first_name = mensaje.from_user.first_name

    response = '{0} {1}'
    bot.send_message(chat_id, response.format(user_first_name, msg_response))


@bot.message_handler(commands=['gay'])
def gay(mensaje):
    '''.'''

    alias_gay(mensaje)


@bot.message_handler(commands=['marico'])
def marico(mensaje):
    '''.'''

    alias_gay(mensaje)


@bot.message_handler(commands=['marisco'])
def marisco(mensaje):
    '''.'''

    alias_gay(mensaje)


@bot.message_handler(commands=['homosexual'])
def homo(mensaje):
    '''.'''

    alias_gay(mensaje)


def alias_gay(mensaje):
    '''.'''

    chat_id = mensaje.chat.id
    user_first_name = mensaje.from_user.first_name

    bot.send_message(chat_id, 'Mas marico sois vos {0}'.format(user_first_name))


@bot.message_handler(commands=['mamamelo'])
def mamamelo(mensaje):
    '''.'''

    chat_id = mensaje.chat.id
    bot.send_message(chat_id, 'Mamamelo vos a mi')


bot.polling(none_stop=True)
