# -*- encoding: utf-8 -*-

from django_telegrambot.apps import DjangoTelegramBot
from sampleproject.celery import app
from time import sleep
from pytube import YouTube
import os

from django.conf import settings
from emoji import emojize
# celery -A pyloro worker -l info

from datetime import datetime
from bs4 import BeautifulSoup
import urllib.request as urllib2
import urllib
import tweepy

@app.task
def pool_message(users, cadena_sin_el_comando):
    for user in users if cadena_sin_el_comando else []:
        try:
            # DjangoTelegramBot.dispatcher.bot.sendMessage(user.get("chat_id"), text=cadena_sin_el_comando)
            print(user.get("chat_id ", cadena_sin_el_comando))
        except Exception as E:
            print(E)
        sleep(3)


@app.task
def grupo_message(grupos, cadena_sin_el_comando):
    for grupo in grupos if cadena_sin_el_comando else []:
        try:
            # DjangoTelegramBot.dispatcher.bot.sendMessage(grupo.get("grupo_id"), text=cadena_sin_el_comando)
            print(grupo.get("grupo_id ", cadena_sin_el_comando))
        except Exception as E:
            print(E)
        sleep(3)


@app.task
def yt2mp3(chat_id, url):
    msg_response = []
    def convert_to_mp3(stream, file_handle):
        import os
        import re
        try:
            nombre = os.path.split(os.path.abspath(file_handle.name))[1]
            print('Nombre', nombre)
            filename = nombre.replace(" ", "_").replace("mp4", "")
            filename_2 = ''.join(re.findall('\w', filename))
            filename_mp3 = "{0}.mp3".format(filename_2)
            comando = 'ffmpeg -i "{0}" -vn -ar 44100 -ac 2 -ab 192 -f mp3 {1}'.format(nombre, filename_mp3)
            print(comando)
            os.system(comando)
            msg_response.append("{0}".format(filename_mp3))
            os.remove(nombre)
        except Exception as E:
            print('error', E)
            os.remove(nombre)
            msg_response.append(":x: <b>Ocurrio un error al procesar el arachivo</b>")
        return msg_response

    yt = YouTube(url)
    yt.register_on_complete_callback(convert_to_mp3)
    yt.streams.filter(only_audio=True).first().download()

    archivo = msg_response[0]
    file_ = open("{0}".format(archivo), "rb")
    DjangoTelegramBot.dispatcher.bot.sendAudio(chat_id,
            audio=file_, caption=archivo)

    file_.close()
    os.remove(archivo)

    #DjangoTelegramBot.dispatcher.bot.sendMessage(chat_id,
    #        parse_mode="html", text=emojize(msg_response[0],
    #            use_aliases=True)
    #        )


def api_tuiter():
    consumer_key = "wz6LRrWGEj0cfOsSqNKLg"
    consumer_secret = "JQUF9IFiFOpzjpTKYxsbKl5QV6o0baoD37fxFpBEE"
    access_token = "23130430-jfgPU8pnQks4AuW5XpS9Wfg3IaYMd4jB88zw8nPm4"
    access_token_secret = "8q9haKn2GrtqDmqMjxRCH0x8UEst1Ckt33AsnJYk"

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    return api

@app.task
def get_price_from_twiter(chat_id, nombre):

    def _validar_condicion(usuario_tuiter, status):
        if usuario_tuiter == 'theairtm':
            if 'Tasa' in status.text and '#Ve' in status.text:
                return True
        elif usuario_tuiter == 'dolarproco':
            if 'PRECIO DEL MERCADO PARALELO' in status.text:
                return True
        elif usuario_tuiter == 'MonitorDolarVe':
            if u'paralelo en Venezuela (en Bs.)' in status.text:
                return True
        else:
            return False
        return False

    def get_stuff(nombre=None):
        api = api_tuiter()
        stuff = tweepy.Cursor(api.user_timeline, screen_name = nombre, include_rts = True)
        return stuff

    def descargar_imagen(nombre, status):
        if _validar_condicion(nombre, status):
            response = ''
            media = status.entities.get('media')
            if media:
                url_imagen = media[0].get('media_url')
                if url_imagen:
                    ruta_imagen_tasa = 'graficos/tasa_{0}.jpg'.format(nombre)
                    urllib2.urlretrieve(url_imagen, ruta_imagen_tasa)
                    # file_ = os.path.join(settings.BASE_DIR, ruta_imagen_tasa)
                    # foto = open(file_, "rb")
                    # bot.sendPhoto(update.message.chat_id, photo=foto)
                    response = ruta_imagen_tasa
            return response

    def get_tweets(stuff, n, nombre):
        for index, status in enumerate(stuff.items(n)):
            today = status.created_at.date()
            response_ruta = descargar_imagen(nombre, status)

            if today == datetime.now().date():
                if response_ruta:
                    response = True, response_ruta
                    break
            else:
                if response_ruta:
                    response =  False, response_ruta
                    break
        return response


    stuff = get_stuff(nombre)
    hoy, ruta_img = get_tweets(stuff, 20, nombre)
    if hoy:
        mensaje = 'Tasa del dia'
    else:
        mensaje = 'Hoy no se ha publicado tasa aun, se muestra la anterior'

    print(settings.BASE_DIR, ruta_img)
    file_ = os.path.join(settings.BASE_DIR, ruta_img)
    foto = open(file_, "rb")
    bot.sendPhoto(chat_id, photo=foto, caption=mensaje)


    # html_page = urllib2.urlopen(url).read()
    # soup = BeautifulSoup(html_page, "html.parser")

    # images = []
    # for img in soup.findAll('img'):
    # images.append(img.get('src'))
    # print(img.get("src"))

