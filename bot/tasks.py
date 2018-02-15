# -*- encoding: utf-8 -*-

from django_telegrambot.apps import DjangoTelegramBot
from sampleproject.celery import app
from time import sleep

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
def yt2mp3(bot, update, url):
    from pytube import YouTube
    import os

    def convert_to_mp3(stream, file_handle):
        import ipdb;ipdb.set_trace()
        try:
            nombre = os.path.split(os.path.abspath(file_handle.name))[1]
            filename = nombre.replace(" ", "_")
            comando = "ffmpeg -i '{0}' -vn -ar 44100 -ac 2 -ab 192 -f mp3 {1}.mp3".format(nombre, filename)
            os.system(comando)
            msg_response = ":bell: {0} Archivo procedo con exito.".foramt(
                    filename)
        except Exception as E:
            print(E)
            msg_response = " :x: <b>Ocurrio un error al procesar el arachivo</b>"

    yt = YouTube(url)
    yt.register_on_complete_callback(convert_to_mp3)
    yt.streams.filter(only_audio=True).first().download()

    DjangoTelegramBot.dispatcher.bot.sendMessage(update.message.chat_id,
            parse_mode="html", text=emojize(msg_response, use_aliases=True))

