# -*- coding: utf-8 -*-
import telebot
from telebot import types
import requests
from scrapy import NoticiasPanorama


TOKEN = '336382255:AAHwrdIgN0j3gIet0xnJfCKs78ojp1dm28s'
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['dameunaayudaitaahi', 'help', 'ayuda', '?', 'ayudame'])
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


""" Hacer reply al mensaje
@bot.message_handler(commands=['si', 'no'])
def send_welcome(message):
        bot.reply_to(message, "Howdy, how are you doing?")
"""


""" Captura todo
@bot.message_handler(func=lambda m: True)
def echo_all(message):
    import ipdb; ipdb.set_trace() # BREAKPOINT
    bot.reply_to(message, message.text)
"""

@bot.inline_handler(lambda query: query.query == 'text')
def query_text(inline_query):
    import ipdb; ipdb.set_trace() # BREAKPOINT
    try:
        r = types.InlineQueryResultArticle('1', 'Result', types.InputTextMessageContent('Result message.'))
        r2 = types.InlineQueryResultArticle('2', 'Result2', types.InputTextMessageContent('Result message2.'))
        bot.answer_inline_query(inline_query.id, [r, r2])
    except Exception as e:
        print(e)

@bot.message_handler(commands=['bitcoin', 'Bitcoin', 'BitCoin', 'BITCOIN', 'btc', 'BTC'])
def bitcoin(mensaje):
    '''.'''

    chat_id = mensaje.chat.id
    user_first_name = mensaje.from_user.first_name

    url = "https://api.coinbase.com/v2/exchange-rates?currency=BTC"
    response = requests.get(url).json().get("data").get("rates").get("USD")

    msg_response = '{0} El precio del Bitcoin es: {1:0,.2f} USD'.format(user_first_name, float(response))
    bot.send_message(chat_id, msg_response)


@bot.message_handler(commands=['calcular', 'calcular', 'CALCULAR', 'calc'])
def calculo(mensaje):
    '''.'''

    parameters = mensaje.text
    chat_id = mensaje.chat.id
    user_first_name = mensaje.from_user.first_name
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
            cadena = 'Teneis que indicar un calculo, Ejemplo: [2+2]'

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


@bot.message_handler(commands=['dolartoday', 'Dolartoday', 'DolarToday', 'dt'])
def dolartoday(mensaje):
    '''.'''

    chat_id = mensaje.chat.id
    user_first_name = mensaje.from_user.first_name

    rq = requests.get('https://s3.amazonaws.com/dolartoday/data.json')
    devuelto = rq.json()
    msg_response = devuelto['USD']['transferencia']

    response = '{0} El precio del paralelo en Vzla es: {1:0,.2f}'
    bot.send_message(chat_id, response.format(user_first_name, float(msg_response)))


@bot.message_handler(commands=['hola', 'hello', 'hi'])
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


@bot.message_handler(commands=['gay', 'marico', 'marisco', 'homosexual', 'maricon'])
def gay(mensaje):
    '''.'''
    chat_id = mensaje.chat.id
    user_first_name = mensaje.from_user.first_name

    bot.send_message(chat_id, 'Mas marico sois vos {0}'.format(user_first_name))


@bot.message_handler(commands=['mamamelo', 'chupamelo'])
def mamamelo(mensaje):
    '''.'''

    chat_id = mensaje.chat.id
    bot.send_message(chat_id, 'Mamamelo vos a mi')


bot.polling(none_stop=True)