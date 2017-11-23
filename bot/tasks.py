# -*- encoding: utf-8 -*-

from django_telegrambot.apps import DjangoTelegramBot
from sampleproject.celery import app
from time import sleep

# celery -A pyloro worker -l info


@app.task
def pool_message(users, cadena_sin_el_comando):
    for user in users if cadena_sin_el_comando else '':
        try:
            # DjangoTelegramBot.dispatcher.bot.sendMessage(user.get("chat_id"), text=cadena_sin_el_comando)
            print(user.get("chat_id ", cadena_sin_el_comando))
        except Exception as E:
            print(E)
        sleep(3)

