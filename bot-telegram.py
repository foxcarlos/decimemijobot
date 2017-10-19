# -*- coding: utf-8 -*-
import telebot
from telebot import types

TOKEN = '336382255:AAHwrdIgN0j3gIet0xnJfCKs78ojp1dm28s'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['hola'])
def comando_hola(mensaje):
    '''.'''

    print(mensaje)
    chat_id = mensaje.chat.id
    user_first_name = mensaje.from_user.first_name

    bot.send_message(chat_id, 'Que fue mijo {0} como estais..?'.format(user_first_name))

@bot.message_handler(commands=['suma'])
def comando_suma(mensaje):
    '''.'''

    chat_id = mensaje.chat.id
    parameters = mensaje.text.split()[1].split(',')
    total_sum = sum([float(n) for n in parameters])
    user_first_name = mensaje.from_user.first_name

    response = 'Ey..! {0} aqui teneis tu suma, {1}, a ver si te comprais una calculadora'
    bot.send_message(chat_id, response.format(user_first_name, total_sum))


@bot.message_handler(commands=['ayudame'])
def comando_suma(mensaje):
    '''.'''

    chat_id = mensaje.chat.id
    msg_response = """

    Lista de Comandos: 
    /suma 2,2,5
    /hola
    /chao
    /ayudame

    """
    user_first_name = mensaje.from_user.first_name

    response = 'Ey..! {0} aqui teneis tu ayuda, {1}'
    bot.send_message(chat_id, response.format(user_first_name, msg_response))

@bot.message_handler(commands=['chao'])
def comando_chao(mensaje):
    '''.'''

    chat_id = mensaje.chat.id
    bot.send_message(chat_id, 'Dala papi nos vemos, cualquier verga gritais')

bot.polling(none_stop = True)


