# -*- encoding: utf-8 -*-

from django_telegrambot.apps import DjangoTelegramBot
from sampleproject.celery import app
from time import sleep
from pytube import YouTube
import os

from emoji import emojize
# celery -A pyloro worker -l info


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
        try:
            nombre = os.path.split(os.path.abspath(file_handle.name))[1]
            print('Nombre', nombre)
            filename = nombre.replace(" ", "_").replace("(", "").replace(")", "")
            filename_mp3 = "{0}.mp3".format(filename)
            comando = "ffmpeg -i '{0}' -vn -ar 44100 -ac 2 -ab 192 -f mp3 {1}".format(nombre, filename_mp3)
            os.system(comando)
            msg_response.append(":bell: {0} Archivo procedo con exito.".format(
                    filename_mp3))
        except Exception as E:
            print('error', E)
            msg_response.append(":x: <b>Ocurrio un error al procesar el arachivo</b>")
        return msg_response

    yt = YouTube(url)
    yt.register_on_complete_callback(convert_to_mp3)
    yt.streams.filter(only_audio=True).first().download()

    file_ = open("bot/static/img/{0}".format(msg_response[0]), "rb")
    bot.sendPhoto(update.message.chat_id,  photo=file_, caption="Si deseas haer una colaboracion de bitcoin puedes hacerlo a la siguiente direccion del wallet 1EXj4afHxArsPesqFfPwYcr522JkYrPcMq")

    DjangoTelegramBot.dispatcher.bot.sendMessage(chat_id,
            parse_mode="html", text=emojize(msg_response[0],
                use_aliases=True)
            )

