#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import requests
import logging
from emoji import emojize

from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, InlineQuery
from django_telegrambot.apps import DjangoTelegramBot
from random import randint

from django.conf import settings

logger = logging.getLogger(__name__)

from django.db.models import Count
from django.contrib.auth.models import User as UserDjango
from bot.scrapy import NoticiasPanorama
from bot.models import Alerta, AlertaUsuario, User, Grupo, Comando, ComandoEstado
from bot.tasks import pool_message
from datetime import datetime

try:
    import numpy as np
except:
    pass

try:
    import matplotlib.pyplot as plt
except:
    pass

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
URL_PRICE_USD = settings.CRIPTO_MONEDAS.get("URL_PRICE_USD")
URL_PRICE_USD_EUR_MARKET = settings.CRIPTO_MONEDAS.get("URL_PRICE_USD_EUR_MARKET")
URL_DOLARTODAY = settings.CRIPTO_MONEDAS.get("URL_DOLARTODAY")


#############################################################################
def cerrar_contrato(bot, update, args):
    contrato_id = args[0] if args else []


def crear_contrato(bot, update, args):

    global buyer_seller
    global operacion
    buyer_seller = []
    operacion = args[0] if args else []

    if not operacion:
        msg_response = ":no_entry_sign: Debes indicar el motivo de la operacion.\n<b>Ej: /trade venta de BTC por USD</b>"
        update.message.reply_text(parse_mode="html",
                text=emojize(msg_response, use_aliases=True))
        return True

    keyboard = [[
            InlineKeyboardButton("Si", callback_data="aceptar"),
            InlineKeyboardButton("No", callback_data="cancelar")]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Desea crear un contrato de compra venta?:',
            reply_markup=reply_markup)
    return True

def callback_button(bot, update):
    query = update.callback_query

    if query.data == "aceptar":
        keyboard = [[InlineKeyboardButton("Soy el Vendedor", callback_data="vendedor"),]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text('Presione este boton solo el <b>vendedor</b>:',
                parse_mode="html",  reply_markup=reply_markup)

    elif query.data == "vendedor":
        a.append(query.from_user.username)
        keyboard = [[InlineKeyboardButton("Soy el Comprador",
            callback_data="comprador"),],]
        reply_markup = InlineKeyboardMarkup(keyboard)

        #query.bot.sendMessage(query.message.chat.id, text="Vendedor:{0}".format(query.from_user.first_name))
        query.edit_message_text('Ahora presione este boton el Comprador:',
                reply_markup=reply_markup)

    elif query.data == "comprador":
        buyer_seller.append(query.from_user.username)
        keyboard = [[
            InlineKeyboardButton("Generar", callback_data="generar"),
            InlineKeyboardButton("Cancelar", callback_data="cancelar_generar")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        #query.bot.sendMessage(query.message.chat.id, text="Comprador:{0}".format(query.from_user.first_name))
        query.edit_message_text('Presione para generar el contrato compra-venta:', reply_markup=reply_markup)

    elif query.data == "generar":
        grupo_id = query.message.chat.id
        grupo_titulo = query.message.chat.title
        contrato = randint(0,9796220)
        # operacion = cadena_sin_el_comando
        comprador = buyer_seller[1]
        vendedor =buyer_seller[0]

        msg_response = """
        :pushpin: <code>Se ha generado un contrato compra-venta:</code>\n
        <b>Contrato:</b><b>{0}</b>
        <b>Operacion:</b> {1}
        <b>Comprador:</b> {2}
        <b>vendedor:</b> {3}
        <b>Grupo:</b> {4}
        <b>Status:</b> En Proceso
        """.format(contrato, operacion, comprador, vendedor, grupo_titulo)

        query.edit_message_text(parse_mode="html", text=emojize(msg_response, use_aliases=True))

    elif query.data == "cancelar_generar":
        query.edit_message_text('Cancelado')

    elif query.data == "cancelar":
        query.edit_message_text('Contrato cancelado:')

    return True

#############################################################################
def grupo_nuevo(update):
    if 'private' == update.message.chat.type:
        return True
    grupo_id = update.message.chat.id
    grupo_titulo = update.message.chat.title
    grupo_tipo = update.message.chat.type

    try:
        grupo = Grupo.objects.update_or_create(grupo_id=grupo_id)[0]
        grupo.descripcion = grupo_titulo
        grupo.tipo = grupo_tipo
        grupo.save()
    except Exception as E:
        print(E)

    return True

def usuario_nuevo(update):
    # Datos del usuario
    id_user = update.message.from_user.id
    usuario = update.message.from_user.username
    nombre = update.message.from_user.first_name if \
            hasattr(update.message.from_user, "first_name") else ""
    apellido = update.message.from_user.last_name if \
            hasattr(update.message.from_user, "lasta_name") else ""
    codigo_leng = update.message.from_user.language_code if\
            hasattr(update.message.from_user, "language_code") else ""

    grupo_nuevo(update)

    try:
        user = User.objects.update_or_create(chat_id=id_user)[0]
        user.username=usuario
        user.first_name=nombre
        user.last_name=apellido
        user.save()

    except Exception as E:
        print(E)

    return True

def valida_autorizacion_comando(bot, update):
    if 'private' == update.message.chat.type:
        return True

    comando = update.message.text
    grupo_id = update.message.chat.id
    es_comando = True if update.message.entities[0].type == 'bot_command' else False

    if es_comando:
        if '@' in comando:
            comando_ejecutado = comando[comando.find('/')+1: comando.find('@')]
        else:
            comando_ejecutado = ''.join(comando.split(" ")[0]).replace('/', "")

        buscar_comando = ComandoEstado.objects.filter(grupo_id=grupo_id,
                comando__nombre=comando_ejecutado)

        if buscar_comando:
            esta_activo = buscar_comando[0].activo
            if not esta_activo:
                return False

    return True

def es_admin(bot, update):
    es_admin = False

    # Si se invoco desde un grupo
    chat_id = update.message.chat.id
    chat_tipo = update.message.chat.type
    chat_username = update.message.chat.username
    chat_first_name = update.message.chat.first_name
    chat_titulo_grupo = update.message.chat.title

    # Quien Ejecuto el comando
    user = update.message.from_user
    id_ = user.id
    username = user.username
    cuenta_real = user.name

    if chat_tipo != "private":
        obj_chat_administradores = bot.get_chat_administrators(chat_id)
        lista_id_admin = [f.user.id for f in obj_chat_administradores]
        es_admin = id_ in lista_id_admin

    return es_admin

def buscar_usuario_id(nombre):
    usuario = User.objects.filter(username__icontains=nombre)
    return usuario.chat_id if usuario else 0

def kick(bot, update):
    if not valida_autorizacion_comando(bot, update):
        # bot.sendMessage(update.message.chat_id, text=emojize("comando desabilitado por el admin", use_aliases=True))
        print('comando esta desactivado')
        return True

    parameters = update.message.text
    cadena_sin_el_comando = ' '.join(parameters.split()[1:])
    usuario = cadena_sin_el_comando.replace('@','')

    if not es_admin(bot, update):
        response = ':no_entry_sign: _{0}_, Solo los usuarios *Admin* pueden usar este comando'.format(update.message.from_user.username)
        bot.sendMessage(update.message.chat_id, parse_mode="Markdown", text=emojize(response, use_aliases=True))
        return True

    if update.message.reply_to_message:
        kick_from_reply(bot, update)
        return True
    else:
        # Se hizo /ban usuario
        response = '*{0}*, Haz un reply de un mensaje de la personas que quieres expulsar y como comentario escribes /kick'.format(update.message.from_user.username)
        bot.sendMessage(update.message.chat_id, parse_mode="Markdown", text=response)

        file_ = open("bot/static/img/ayuda_ban_uso.png", "rb")
        bot.sendPhoto(update.message.chat_id,  photo=file_, caption="Ejemplo de uso del comando /kick")

def kick_from_reply(bot, update):
    id_usuario_ban = update.message.reply_to_message.from_user.id
    username_usuario_ban = update.message.reply_to_message.from_user.username

    if id_usuario_ban:
        print(datetime.now())
        fecha = datetime.timestamp(datetime.now())+31
        print(fecha)
        update.message.chat.kick_member(id_usuario_ban, fecha)

        response = ' :boom: Fuistes expulsado :rocket: del grupo por *{0}*'.format(update.message.from_user.username)
        bot.sendMessage(id_usuario_ban, parse_mode="Markdown", text=emojize(response, use_aliases=True ))
        response = 'Usuario *{0}* expulsado :rocket: por _{1}_ :smiling_imp:'.format(username_usuario_ban, update.message.from_user.username)
    else:
        response = ':x: No fue posible expulsar el usuario {0} con el id {1}'.format(username_usuario_ban, id_usuario_ban)

    bot.sendMessage(update.message.chat_id, parse_mode="Markdown", text=emojize(response, use_aliases=True))
    return True

def ban(bot, update):
    if not valida_autorizacion_comando(bot, update):
        # bot.sendMessage(update.message.chat_id, text=emojize("comando desabilitado por el admin", use_aliases=True))
        return True

    parameters = update.message.text
    cadena_sin_el_comando = ' '.join(parameters.split()[1:])
    usuario = cadena_sin_el_comando.replace('@','')

    if not es_admin(bot, update):
        response = ':no_entry_sign: _{0}_, Solo los usuarios *Admin* pueden usar este comando'.format(update.message.from_user.username)
        bot.sendMessage(update.message.chat_id, parse_mode="Markdown", text=emojize(response, use_aliases=True))
        return True

    if update.message.reply_to_message:
        ban_from_reply(bot, update)
        return True
    else:
        # Se hizo /ban usuario
        response = '*{0}*, Haz un reply de un mensaje de la personas que quieres expulsar y como comentario escribes /ban'.format(update.message.from_user.username)
        bot.sendMessage(update.message.chat_id, parse_mode="Markdown", text=response)

        file_ = open("bot/static/img/ayuda_ban_uso.png", "rb")
        bot.sendPhoto(update.message.chat_id,  photo=file_, caption="Ejemplo de uso del comando /ban")
      # ban_directo(bot, update)

def ban_from_reply(bot, update):
    id_usuario_ban = update.message.reply_to_message.from_user.id
    username_usuario_ban = update.message.reply_to_message.from_user.username

    if id_usuario_ban:
        update.message.chat.kick_member(id_usuario_ban)
        response = ' :boom: Fuistes expulsado :rocket: del grupo por *{0}*'.format(update.message.from_user.username)
        bot.sendMessage(id_usuario_ban, parse_mode="Markdown", text=emojize(response, use_aliases=True ))
        response = 'Usuario *{0}* expulsado :rocket: por _{1}_ :smiling_imp:'.format(username_usuario_ban, update.message.from_user.username)
    else:
        response = ':x: No fue posible expulsar el usuario {0} con el id {1}'.format(username_usuario_ban, id_usuario_ban)

    bot.sendMessage(update.message.chat_id, parse_mode="Markdown", text=emojize(response, use_aliases=True))
    return True

def unban(bot, update):
    parameters = update.message.text
    cadena_sin_el_comando = ' '.join(parameters.split()[1:])
    usuario = cadena_sin_el_comando.replace('@','')
    response = ''

    if es_admin(bot, update):
        print('Es Administrador')
        id_usuario = buscar_usuario_id(usuario)
        if id_usuario:
            update.message.chat.kick_member(id_usuario)
            response = 'Usuario {0} expulsado por {1}'.format(usuario, update.message.from_user.username)
        else:
            response = 'No fue posible desbanear el usuario {0} con el id {1}'.format(usuario, id_usuario)
    else:
        response = '_{0}_, Solo los usuarios *Admin* pueden usar este comando'.format(update.message.from_user.username)

    bot.sendMessage(update.message.chat_id, parse_mode="Markdown", text=response)
    return True

"""
def prueba_boton(bot, update):
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup

    import ipdb; ipdb.set_trace() # BREAKPOINT
    # chat_administradores = update.message.chat.get_administrators()
    keyboard = [[InlineKeyboardButton("Option 1", callback_data='1'),
                 InlineKeyboardButton("Option 2", callback_data='2')],
                [InlineKeyboardButton("Option 3", callback_data='3')]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Seleccione una Opccion:', reply_markup=reply_markup)

def callback_button(bot, update):
    query = update.callback_query

    bot.edit_message_text(text="La opcion fue: {}".format(query.data),
            chat_id=query.message.chat_id,
            message_id=query.message.message_id
            )
    if query.data == '2':
        reply_markup = opcion2_boton(bot, update)
        # editMessageReplyMarkup
        query.edit_message_text('Seleccione otra Opccion:', reply_markup=reply_markup)
    return True

def opcion2_boton(bot, update):
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup

    # chat_administradores = update.message.chat.get_administrators()
    keyboard = [[InlineKeyboardButton("Option 2.1", callback_data='2.1'),
                 InlineKeyboardButton("Option 2.2", callback_data='2.2')],
                [InlineKeyboardButton("Option 2.3", callback_data='2.3')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup

def prueba_forcereply(bot, update):
    update.message.reply_text('Cual es tu nombre:')

def call_ForceReply(bot, update):
    query = update.force_reply
"""

def ayuda_set_alarma():
    response = """
    Te doy una mano con eso:

    - Las Alarmas son:

    - set_alarma_bitcoin
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
    return response


def button_alarmas(bot, update):
    response = ""
    username = update.callback_query.from_user.username
    chat_id = update.callback_query.from_user.id
    texto = update.callback_query.message.text
    alerta = texto[texto.find("[", 0)+1: texto.find("]", 1)]

    query = update.callback_query

    def activar_desactivar(estado):
        if update.callback_query.message.chat.type == 'private':
            username = update.callback_query.message.chat.username
            chat_id = update.callback_query.message.chat.id

        elif update.callback_query.message.chat.type == 'group':
            username = update.callback_query.message.chat.title
            chat_id = update.callback_query.message.chat.id

        elif update.callback_query.message.chat.type == 'supergroup':
            username = update.callback_query.message.chat.username
            chat_id = update.callback_query.message.chat.id

        obj_alerta = Alerta.objects.get(comando__icontains=alerta)
        buscar_o_crear = AlertaUsuario.objects.get_or_create(
                alerta=obj_alerta, chat_id=chat_id)[0]

        buscar_o_crear.estado = estado
        buscar_o_crear.chat_username = username
        buscar_o_crear.save()
        response = "{0} Alarma <b>{1}</b> <i>{2}</i>".format(
                ':bell:' if estado=='A' else ':no_bell:',
                alerta,
                'Activada' if estado=='A' else 'Desactivada')
        return response

    if query.data == 'Activar':
        response = activar_desactivar('A')

    elif query.data == 'Desactivar':
        response = activar_desactivar('I')

    elif query.data == 'Ayuda':
        response =  ayuda_set_alarma()

    elif query.data == 'Cancelar':
        response = "Comando cancelado"

    bot.edit_message_text(parse_mode="HTML", text=emojize(response, use_aliases=True),
            chat_id=query.message.chat_id,
            message_id=query.message.message_id)


def get_price(url):
    return requests.get(url).json().get("data").get("rates").get("USD")


def get_price_coinmarketcap(url):
    return requests.get(url).json()[0].get("price_usd")


def all_coins(bot, update):
    # bot.sendMessage(update.message.chat_id, text="Consultando... En un momento te muestro la informacion...!")
    bot.sendChatAction(update.message.chat_id, "upload_document")

    btc = get_price(URL_BTC_USD)
    eth = get_price(URL_ETH_USD)
    ltc = get_price(URL_LTC_USD)
    bcc = get_price_coinmarketcap(URL_BCH_USD)
    das = get_price_coinmarketcap(URL_DAS_USD)
    btg = get_price_coinmarketcap(URL_BTG_USD)
    xmr = get_price_coinmarketcap(URL_XMR_USD)
    xrp = get_price_coinmarketcap(URL_XRP_USD)

    response = """:speaker: Cripto Monedas hoy (Coinbase ):\n\n\
    :dollar: *BTC*={0:0,.2f}\n\
    :dollar: *ETH*={1:0,.2f}\n\
    :dollar: *LTC*={2:0,.2f}\n\
    :dollar: *BTCASH*={3:0,.2f}\n\
    :dollar: *DASH*={4:0,.2f}\n\
    :dollar: *BTGOLD*={5:0,.2f}\n\
    :dollar: *RIPPLE*={6:0,.2f}\n\
    :dollar: *MONERO*={7:0,.2f}""".format(
                    float(btc),
                    float(eth),
                    float(ltc),
                    float(bcc),
                    float(das),
                    float(btg),
                    float(xrp),
                    float(xmr)
                    )

    bot.sendMessage(update.message.chat_id, parse_mode="Markdown", text=emojize(response, use_aliases=True))
    usuario_nuevo(update)


def get_price_usd_eur(coin_ticker, market='coinbase'):
    url = URL_PRICE_USD_EUR_MARKET.format(coin_ticker.upper(), market)
    data = requests.get(url)
    response = data.json() if data else ''
    return response


def calc(bot, update):
    print(update.message)
    market = 'coinbase'
    parameters = update.message.text
    cadena_sin_el_comando = ' '.join(parameters.split()[1:])
    params = cadena_sin_el_comando.split() if \
            len(cadena_sin_el_comando.split()) == 2 else []

    if not params:
        response = "*{0}* Debes indicar */clc coin_ticker monto*\n\n_Ej_: /clc btc 0.0002 \n\nSi desea calcular VEF a bitcoin y Dolar ejecute\n\n/clc vef 2500000".format(":question:")
    else:
        moneda, monto = params
        data = get_price_usd_eur(moneda, market)
        if data.get('Response') != "Error":
            total_dolar, total_euros = [float(symbol)*float(monto) for symbol in data.values()]
            total_vef = float(monto) * (data.get("USD") * get_dolartoday())
            response = """:moneybag: El calculo de {3} es :\n\n:dollar: Dolar: {0:,.2f}\n:euro: Euro: {1:,.2f}\n:small_orange_diamond:  VEF: {2:,.2f}\n\nNota: Precios basados en: {4} y VEF en (DolarToday) """.format(
                    total_euros, total_dolar, total_vef, monto, market.capitalize())

        if moneda.upper() == "VEF":
            data = get_price_usd_eur("btc", market)
            total_btc = float(monto) / (data.get("USD") * get_dolartoday())
            total_dolar = float(monto) / get_dolartoday()

            response = """:moneybag: El calculo para {0} es de :\n\n:chart_with_downwards_trend: BTC: {1:,.9f}\n:dollar: Dolares: {2:,.2f}\n\nNota: Precios basados en: {3} y VEF en (DolarToday) """.format(
                monto, total_btc, total_dolar, market.capitalize())

    bot.sendMessage(update.message.chat_id, parse_mode="Markdown", text=emojize(response,
        use_aliases=True))
    # bot.sendMessage(update.message.chat_id, "<b>This</b> <i>is some Text</i>", DjangoTelegramBot.ParseMode.HTML)
    usuario_nuevo(update)


def preparar_prametros(cabecera, valor):
    cabecera = cabecera
    valores = valor
    return dict(zip(cabecera, valores))


def get_historico(lista_params):
    msg_response = False
    if lista_params:
        cabecera = ["coin_ticker", "market", "usd_eur", "dias"]
        valores = lista_params
        params = preparar_prametros(cabecera, valores)

        coin_ticker = params.get("coin_ticker")
        market = params.get("market")
        limite = params.get("dias")
        usd_eur = params.get("usd_eur")

        param0 = "https://min-api.cryptocompare.com/data/histoday?"
        param1 = "fsym={}".format(coin_ticker.upper() if coin_ticker else "BTC")
        param2 = "&tsym={}".format(usd_eur.upper() if usd_eur else "USD")
        param3 = "&limit={}".format(limite if limite else "30")
        param4 = "&aggregate=3"
        param5 = "&e={}".format(market if market else "coinbase")

        url = "{0}{1}{2}{3}{4}{5}".format(
                param0.strip(),
                param1.strip(),
                param2.strip(),
                param3.strip(),
                param4.strip(),
                param5.strip())
        print(url)

        hist = requests.get(url).json()
        if hist.get("Response").lower() == "Error":
            msg_response = False  # hist.get("message")
        else:
            historial = hist.get("Data")
            close = [f.get("close") for f in historial]
            fecha = [datetime.fromtimestamp(f.get("time")) for f in historial]

            plt.rcParams['axes.facecolor'] = 'black'
            lines = plt.plot(fecha, close)
            labels = [f.strftime("%b %d") for f in fecha]
            plt.subplots_adjust(bottom=0.25)
            plt.xticks(fecha, labels, rotation='vertical')

            plt.setp(lines, color='y', linewidth=2.0)
            plt.xlabel("Fecha", fontsize=14, color='blue')
            plt.ylabel("Precio", fontsize=14, color='blue')
            plt.title("Grafico Coin:{0} Market:{1} Moneda:{2}".format(
                coin_ticker.upper() if coin_ticker else 'BTC',
                market.upper() if market else 'coinbase',
                usd_eur.upper() if usd_eur else 'USD'
                ))
            plt.grid(True)
            plt.savefig('graficos/grafico')
            plt.clf()
            msg_response = True

        # /hist <coin_ticker> <market> <usd o eur> <dias>
        return msg_response


def historico(bot, update):
    if not valida_autorizacion_comando(bot, update):
        # bot.sendMessage(update.message.chat_id, text=emojize("comando desabilitado por el admin", use_aliases=True))
        return True

    print(update.message)
    parameters = update.message.text
    cadena_sin_el_comando = ' '.join(parameters.split()[1:])

    params = cadena_sin_el_comando.split() if \
            cadena_sin_el_comando else []

    if get_historico(params):
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        file_ = os.path.join(settings.BASE_DIR, 'graficos/grafico.png')
        foto = open(file_, "rb")
        bot.sendPhoto(update.message.chat_id, photo=foto)
    else:
        response = "{0} Ayuda /grafico <coin_ticker> <market> <usd o eur> <dias>".format(":question:")
        bot.sendMessage(update.message.chat_id, text=emojize(response, use_aliases=True))
        bot.sendMessage(update.message.chat_id, text=emojize("o tambien puedes graficar", use_aliases=True))
        response = "{0} Ayuda /grafico <coin_ticker> <market>".format(":question:")
        bot.sendMessage(update.message.chat_id, text=emojize(response, use_aliases=True))



def price(bot, update):
    print(update.message)
    parameters = update.message.text
    cadena_sin_el_comando = ' '.join(parameters.split()[1:])

    params = cadena_sin_el_comando.split() if \
            len(cadena_sin_el_comando.split()) in range(1,3) else []

    if params:
        coin_ticker, market = params if len(params)>=2 else (''.join(params), '')
        prepare_coin_ticker = "?fsym={0}&tsym=USD".format(coin_ticker.upper())
        url = "{0}{1}".format(URL_PRICE_USD, prepare_coin_ticker)

        inf_btc = requests.get(url).json().get("Data")
        exchanges_btc = inf_btc.get("Exchanges")


    if not cadena_sin_el_comando:
        response = "*{0}* Debes indicar _/precio modena y market_ Ej: */precio btc bitfinex*".format(":question:",
                cadena_sin_el_comando.upper())
        bot.sendMessage(update.message.chat_id, parse_mode="Markdown", text=emojize(response, use_aliases=True))
        return False

    if not exchanges_btc:
        response = "{0} Moneda '{1}' no encontrada, indique las siglas Ej: btc ".format(":x:", cadena_sin_el_comando.upper())
        bot.sendMessage(update.message.chat_id, text=emojize(response, use_aliases=True))
        return False

    exchanges = [market] if market else ['coinbase', 'bitfinex', 'localbitcoins',
            'bittrex', 'poloniex', 'bitstamp', 'kraken', 'hitbtc']

    bloques = inf_btc.get("BlockNumber")
    hash_seg = inf_btc.get("NetHashesPerSecond")
    total_minado = inf_btc.get("TotalCoinsMined")
    block_reward = inf_btc.get("BlockReward")

    response = ":orange_book: CriptoMoneda:{0}:\n\nNro Bloques:{1}\nHash por Seg:{2}\nTotal Minado:{3}\nBlockReward:{4}".format(
            cadena_sin_el_comando.upper(),
            bloques,
            hash_seg,
            total_minado,
            block_reward
            )
    icon = ":bar_chart:"

    for exchange in exchanges_btc:
        moneda = exchange.get('TOSYMBOL')
        market = exchange.get('MARKET')
        precio = exchange.get('PRICE')
        h24h = exchange.get('HIGH24HOUR')
        h24l = exchange.get('LOW24HOUR')
        open24h = exchange.get('OPEN24HOUR')
        volumen = exchange.get('VOLUME24HOUR')

        if market.lower() in exchanges:
            response += """
                    {0} *{1}*\n\
                    USD:{2:0,.2f}\n\
                    24h H:{3:0,.2f}\n\
                    24h L:{4:0,.2f}\n\
                    Volum:{5:0,.2f}
                    """.format(
                            icon,
                            market,
                            float(precio),
                            float(h24h),
                            float(h24l),
                            float(volumen))

    bot.sendMessage(update.message.chat_id, parse_mode = "Markdown", text=emojize(response,
        use_aliases=True))
    usuario_nuevo(update)


def autor(bot, update):
    url = "https://gitlab.com/foxcarlos"
    response = """
    Realizado por @FoxCarlos:

    {0}""".format(url)
    bot.sendMessage(update.message.chat_id, text=response)


def bitcoin(bot, update):
    print(update.message)
    user_first_name = update.message.from_user.first_name

    btc = get_price(URL_BTC_USD)
    response = '*{0}* El precio del Bitcoin es: *{1:0,.2f}* USD'.\
            format(user_first_name, float(btc))
    bot.sendMessage(update.message.chat_id, parse_mode="Markdown", text=response)
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


def evaluar(palabra):
    response = ""
    try:
        response = str(eval(palabra.lower().replace('x', '*'))) + " "
    except Exception as inst:
        response = ""
    return response

def chat(bot, update):
    print(update.message)
    bot.sendMessage(update.message.chat_id,
            text='This chat information:\n {}'.format(update.effective_chat))


def get_dolartoday():
    rq = requests.get('https://s3.amazonaws.com/dolartoday/data.json').json()
    msg_response = rq.get('USD').get('transferencia')
    return msg_response


def get_dolartoday2():
    rq = requests.get(URL_DOLARTODAY).json()

    dolartoday = float(rq.get('USD').get('transferencia'))
    implicito =  float(rq.get("USD").get("efectivo"))
    dicom = float(rq.get("USD").get("sicad2"))
    cucuta = float(rq.get("USD").get("efectivo_cucuta"))
    localbitcoin = float(rq.get("USD").get("localbitcoin_ref"))
    barril = float(rq.get("MISC").get("petroleo").replace(",", ".") )
    oro = float(rq.get("GOLD").get("rate"))
    fecha = datetime.now().strftime("%d-%m-%Y")

    response = """:speaker: DolarToday hoy: {0}:\n\n\
    :dollar: *DolarToday*: {1:0,.2f}\n\
    :dollar: *Implicito*: {2:0,.2f}\n\
    :dollar: *Dicom*: {3:0,.2f}\n\
    :dollar: *Cucuta*: {4:0,.2f}\n\
    :dollar: *LocalBitcoin*: {5:0,.2f}\n\n\
    :fuelpump: *Petroleo*: {6:0,.2f}\n\
    :moneybag: *Oro*: {7:0,.2f}\n\
        """.format(fecha,
                    dolartoday,
                    implicito,
                    dicom,
                    cucuta,
                    localbitcoin,
                    barril,
                    oro)
    return response


def dolartoday(bot, update):
    print(update.message)
    user_first_name = update.message.from_user.first_name
    bot.sendMessage(update.message.chat_id, parse_mode="Markdown", text=emojize(get_dolartoday2(),
        use_aliases=True )
        )
    usuario_nuevo(update)


def enviar_mensajes_todos(bot, update):
    print(update.message)
    parameters = update.message.text
    cadena_sin_el_comando = ' '.join(parameters.split()[1:])

    if valida_root(update):
        users = User.objects.values('chat_id').annotate(dcount=Count('chat_id'))
        pool_message.delay(list(users), cadena_sin_el_comando)



def help(bot, update):
    msg_response = """
    Lista de Comandos:

    /allcoins - Precios de varias criptos
    /bitcoin - Muestra el Precio(segun coinbase)
    /dolartoday

    /set_alarma_bitcoin - Configura alertas
    /set_alarma_ethereum - Configura alertas
    /set_alarma_litecoin - Configura alertas
    /set_alarma_dolartoday - Configura alertas

    /precio <coin_ticker> <market> - Ej: /precio btc coinbase
    /precio <coin_ticker> - Ej: /precio btc

    /help - Ayuda
    /donar - Si deseas hacerme alguna donacion

    /clc - <coin_ticker> <monto> Ej: /clc btc 0.1

    /grafico <coin_ticker> <market> <usd o eur> <dias>
    /grafico <coin_ticker> <market> <usd>
    /grafico <coin_ticker> <market>

    /ban Expulsa a un usuario sin derecho a regresar
    /kick Expulsa a un uusario y puede volver cuando lo desee

    Nota: Ahora es posible hacer calculos 
    con solo escribir directamente 2+2*3

    """
    user_first_name = update.message.from_user.first_name
    user_chat_id = update.message.from_user.id

    if valida_permiso_comando(bot, update):
        user_chat_id = update.message.chat_id
    else:
        user_chat_id = update.message.chat_id
        # response = "{0}, Te envie la informacion al privado".format(user_first_name)
        # bot.sendMessage(user_chat_id, text=response)
        user_chat_id = update.message.from_user.id

    response = '{0} - {1}'.format(user_first_name, msg_response)
    bot.sendMessage(user_chat_id, text=response)
    usuario_nuevo(update)


def me(bot, update):
    print(update.message)
    bot.sendMessage(update.message.chat_id,
            text='Tu informacion:\n{}'.format(update.effective_user))

def valida_permiso_comando(bot, update):
    response = False
    if update.message.chat.type == 'private':
        response = True
    else:
        if es_admin(bot, update):
            response = True
        else:
            texto = ":no_entry_sign: Lo siento, solo los Admin del grupo pueden ejecutar este comando, \n:speaker: Intenta hacerlo en privado al bot https://t.me/DecimeMijobot/?start=true"
            bot.sendMessage(update.message.chat_id, text=emojize(texto, use_aliases=True))
            response = False
    return response

def set_alarma_dolartoday(bot, update):
    if valida_permiso_comando(bot, update):
        set_alarma(bot, update, "dolartoday")

def set_alarma_bitcoin(bot, update):
    if valida_permiso_comando(bot, update):
        set_alarma(bot, update, "bitcoin")

def set_alarma_ethereum(bot, update):
    if valida_permiso_comando(bot, update):
        set_alarma(bot, update, "ethereum")

def set_alarma_litecoin(bot, update):
    if valida_permiso_comando(bot, update):
        set_alarma(bot, update, "litecoin")

def set_alarma(bot, update, alerta):
    response = ""
    parameters = update.message.text

    if update.message.chat.type == 'private':
        username = update.message.from_user.username
        chat_id = update.message.from_user.id

    elif update.message.chat.type == 'group':
        username = update.message.chat.title
        chat_id = update.message.chat.id

    elif update.message.chat.type == 'supergroup':
        username = update.message.chat.username
        chat_id = update.message.chat.id


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
        keyboard = [[InlineKeyboardButton("Activar", callback_data='Activar'),
                    InlineKeyboardButton("Desactivar", callback_data='Desactivar')],
                    [InlineKeyboardButton("Ayuda", callback_data='Ayuda'),
                    InlineKeyboardButton("Regresar", callback_data='Cancelar')]]

        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('No indicastes ninguna opcion para [{0}], que deseas hacer?:'.format(alerta), reply_markup=reply_markup)
        return True

    bot.sendMessage(update.message.chat_id, text=response)
    usuario_nuevo(update)

def valida_root(update):
    print(update.message)
    root = UserDjango.objects.filter(username__icontains="foxcarlos")
    me_id = update.message.chat_id

    if root[0] and root[0].first_name == str(me_id):
        return True
    else:
        return False

def reglas(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Lo siento, Aun se definen las reglas del grupo.")

def nuevo_miembro(bot, update):
    grupo = update.message.chat
    nuevo_usuario = update.message.new_chat_member

    id_ = nuevo_usuario.id
    username = nuevo_usuario.username
    nombre = nuevo_usuario.first_name
    msg_html = """
    *Bienvenido {0} al grupo {1}*\n
    :small_blue_diamond: Id: *{2}*\n
    :small_blue_diamond: Usuario: *{3}*\n
    :small_blue_diamond: Nombre: *{4}*\n
    """.format(username, grupo.title, id_, username, nombre)
    if not username:
        msg_html+= "*{0}* Por politicas del Grupo es necesario que configures un alias @{1}\n".format(nombre, id_)

    bot.send_message(chat_id=update.message.chat_id, parse_mode = "Markdown", text=emojize(msg_html, use_aliases=True))
    usuario_nuevo(update)

def abandono_grupo(bot, update):
    grupo = update.message.chat
    nuevo_usuario = update.message.left_chat_member

    id_ = nuevo_usuario.id
    username = nuevo_usuario.username
    nombre = nuevo_usuario.first_name
    msg_html = """
    <b>Ups..!  {0} salio del grupo {1} </b>

    <ul>
        <li>Id: {0}</li>
        <li>Usuario: {2}/li>
        <li>Nombre: {3}</li>
    </ul> """.format(username, grupo.title, username, nombre)

    bot.send_message(chat_id=update.message.chat_id, parse_mode = "html", text=msg_html)
def hacer_donacion(bot, update):
    file_ = open("bot/static/img/bitcoin:1EXj4afHxArsPesqFfPwYcr522JkYrPcMq?recv=LocalBitcoins.com.png", "rb")
    bot.sendPhoto(update.message.chat_id,  photo=file_, caption="Si deseas haer una colaboracion de bitcoin puedes hacerlo a la siguiente direccion del wallet 1EXj4afHxArsPesqFfPwYcr522JkYrPcMq")
    return True

def start(bot, update):
    # print(update.message)
    bot.sendMessage(update.message.chat_id,
            text='Bienvenido, te invito a ejecutar el comando /help para obtener mas ayuda')
    usuario_nuevo(update)

def startgroup(bot, update):
    print(update.message)
    bot.sendMessage(update.message.chat_id,
            text='Bienvenido al grupo, te invito a ejecutar /reglas para conocer las reglas principales del grupo,\
            /help para obtener mas ayuda')
    usuario_nuevo(update)

def error(bot, update, error):
    print(error)
    logger.warn('Update "%s" caused error "%s"' % (update, error))

def forwarded(bot, update):
    print(update.message)
    #bot.sendMessage(update.message.chat_id,
    #        text='This msg forwaded information:\n {}'.\
    #                format(update.effective_message))

def echo(bot, update):
    print("Eco")
    print(update.message)
    m = evaluar(update.message.text)
    if m:
        update.message.reply_text(m)
    usuario_nuevo(update)

def unknown(bot, update):
    # bot.send_message(chat_id=update.message.chat_id, text="Lo siento, No reconozco ese comando.")
    pass


def main():
    logger.info("Loading handlers for telegram bot")

    # Default dispatcher (this is related to the first bot in settings.TELEGRAM_BOT_TOKENS)
    dp = DjangoTelegramBot.dispatcher
    # To get Dispatcher related to a specific bot
    # dp = DjangoTelegramBot.getDispatcher('BOT_n_username')  #get by bot username

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("reglas", reglas))
    dp.add_handler(CommandHandler("ban", ban))
    dp.add_handler(CommandHandler("kick", kick))
    dp.add_handler(CommandHandler("unban", unban))

    dp.add_handler(CommandHandler("trade", crear_contrato))
    dp.add_handler(CallbackQueryHandler(callback_button))

    dp.add_handler(CommandHandler("tradeclose", cerrar_contrato, pass_args=True))
    # dp.add_handler(InlineQueryHandler(reply_to_query))

    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("ayuda", help))
    dp.add_handler(CommandHandler("?", help))

    dp.add_handler(CommandHandler("allcoins", all_coins))
    dp.add_handler(CommandHandler("precio", price))
    dp.add_handler(CommandHandler("p", price))

    dp.add_handler(CommandHandler("grafico", historico))
    dp.add_handler(CommandHandler("graf", historico))
    dp.add_handler(CommandHandler("graph", historico))
    dp.add_handler(CommandHandler("chart", historico))

    dp.add_handler(CommandHandler("calc", calc))
    dp.add_handler(CommandHandler("clc", calc))

    dp.add_handler(CommandHandler("bitcoin", bitcoin))
    dp.add_handler(CommandHandler("satoshitango", bitcoin_satoshitango))
    dp.add_handler(CommandHandler("set_alarma_bitcoin", set_alarma_bitcoin))
    dp.add_handler(CallbackQueryHandler(button_alarmas))

    dp.add_handler(CommandHandler("set_alarma_dolartoday", set_alarma_dolartoday))
    dp.add_handler(CommandHandler("set_alarma_ethereum", set_alarma_ethereum))
    dp.add_handler(CommandHandler("set_alarma_litecoin", set_alarma_litecoin))
    dp.add_handler(CommandHandler("dolartoday", dolartoday))
    dp.add_handler(CommandHandler("masivo", enviar_mensajes_todos))
    dp.add_handler(CommandHandler("autor", autor))
    dp.add_handler(CommandHandler("donar", hacer_donacion))
    dp.add_handler(CommandHandler("startgroup", startgroup))
    dp.add_handler(CommandHandler("me", me))
    dp.add_handler(CommandHandler("chat", chat))
    dp.add_handler(MessageHandler(Filters.forwarded, forwarded))

    dp.add_handler(MessageHandler(Filters.command, unknown))
    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))
    # dp.add_handler(MessageHandler(Filters.status_update, abandono_grupo))
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, nuevo_miembro))

    # log all errors
    dp.add_error_handler(error)

