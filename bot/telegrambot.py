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
from django.db.models import Count, Q
from django.contrib.auth.models import User as UserDjango
from django.core.exceptions import ObjectDoesNotExist

from bot.scrapy import NoticiasPanorama
from bot.models import Alerta, AlertaUsuario, User, Grupo, Comando, ComandoEstado, Contrato, PersonaContrato

from bot.tasks import pool_message
from datetime import datetime

logger = logging.getLogger(__name__)

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

global buyer_seller
global inf_operacion

buyer_seller = []
inf_operacion = []

def ayuda_trade():
    help_trade = """
    <b>Ayuda de Comandos</b>\n
    /trade - Crea un contrato

    /tradec - Califica el Contrato
    Ej /tradec contrato comentario

    /tradeb  - Busca Inf contrato
    Ej /tradeb contrato

    /traderef - Referencias de usuario
    Ej /traderef username\n

    :bulb: <b>Modo de uso:</b>

    1) Crear un conrtato
    2) <i>Hacer el intercambio</i>
    3) Califica el contrato\n
    <b>Nota:</b> Cuando ambas
    partes hayan calificado
    el contrato se enviara
    la informacion al grupo
    desde donde se creo el
    contrato y este sera
    <b>cerrado</b> automaticamente
    """
    return help_trade

def buscar_user(bot, update, args):
    lista_user = []
    entidades = update.message.entities[1:]
    for index, entidad in enumerate(entidades):
        if entidad.type == 'text_mention':
            user_chat_id = entidad.user.id
            try:
                usuario = User.objects.get(chat_id=user_chat_id)
                lista_user.append(usuario)
            except ObjectDoesNotExist:
                pass
        elif entidad.type == 'mention':
            user_ = args[index].replace('@', '')
            try:
                usuario = User.objects.get(
                        username__icontains=user_)
                lista_user.append(usuario)
            except ObjectDoesNotExist:
                pass
    return lista_user

def trade2user(bot, update, args):
    if len(args) <1:
        msg_response = """
        :no_entry_sign: Debes mencionar la persona a quien quieres consultar\n:bulb: Ejemplo:\n
        <b>/trade2user @FoxCarlos</b>\n
        Ejecuta <b>/trade ?</b>
        para obtener mas ayuda"""
        update.message.reply_text(parse_mode="html",
                text=emojize(msg_response, use_aliases=True))
        return False

    usuarios = buscar_user(bot, update, args)
    lista_contratos = PersonaContrato.objects.filter(user=usuarios[0])
    detalle_contratos = PersonaContrato.objects.filter(
            contrato__in=[
                contrato.contrato for contrato in lista_contratos]).exclude(
                        user=usuarios[0])
    msg_response = ''
    for fila in detalle_contratos:
        msg_response += """<code>Intercambios de</code> <b>{7}</b>\n:small_blue_diamond:<b>Fecha:</b> <code>{0}</code>\n:small_blue_diamond:<b>Contrato:</b> <code>{1}</code>\n:small_blue_diamond:<b>Operacion:</b> <code>{2}</code>\n:small_blue_diamond:<b>Grupo:</b> <code>{3}</code>\n:small_blue_diamond:<b>Cliente:</b> <code>{4}</code>\n:small_blue_diamond:<b>Puntuacion:</b> <code>{5}</code>\n:small_blue_diamond:<b>Comentario:</b> <code>{6}</code>\n\n
        """.format(
                fila.contrato.fecha.strftime("%d-%m-%Y"),
                fila.contrato.contrato,
                fila.contrato.operacion,
                fila.contrato.grupo.descripcion,
                fila.user.first_name,
                fila.puntuacion,
                fila.comentario,
                usuarios[0].username
                )
    update.message.reply_text(parse_mode="html",
            text=emojize(msg_response, use_aliases=True))


def trade_referencia(bot, update, args):
    chat_id = update.message.from_user.id
    if len(args) <1:
        msg_response = """
        :no_entry_sign: Debes mencionar la persona a quien quieres consultar\n:bulb: Ejemplo:\n
        <b>/traderef @FoxCarlos</b>\n
        Ejecuta <b>/trade ?</b>
        para obtener mas ayuda"""
        update.message.reply_text(parse_mode="html",
                text=emojize(msg_response, use_aliases=True))
        return False

    usuarios = buscar_user(bot, update, args)
    print(usuarios)
    msg_response = ''
    msg_response_cabecera = ''
    msg_response_final = ''

    def puntuacion(total, pos):
        puntua = (pos - (pos/100)) / total
        return '{0}%'.format(round(puntua, 1)*100)

    for usuario in usuarios:
        msg_response_cabecera = ''
        msg_response = ''
        msg_response_final = ''
        puntos_negativos = 0

        # get_contratos  = PersonaContrato.objects.filter(user=usuario)
        lista_contratos = [f.contrato \
                for f in PersonaContrato.objects.filter(
                    user=usuario)]
        get_contratos = PersonaContrato.objects.filter(
                contrato__in=lista_contratos).exclude(user=usuario)

        total_intercambios = get_contratos.count()
        agrupar = get_contratos.values('puntuacion').annotate(dcount=Count(
            'puntuacion'))

        nombre = usuario.username if usuario.username else usuario.first_name

        for f in agrupar:
            if f.get('puntuacion') == 'pos':
                msg_response+=':small_blue_diamond: Positivo: {0}\n'.format(f.get('dcount'))
            elif f.get('puntuacion') == 'neg':
                msg_response+=':small_blue_diamond: Negativo: {0}\n'.format(f.get('dcount'))
                puntos_negativos = f.get('dcount')
            elif f.get('puntuacion') == 'neu':
                msg_response+=':small_blue_diamond: Neutral: {0}\n'.format(f.get('dcount'))
            else:
                continue

        msg_response_cabecera = """:memo: Calificaion para <b>{0} {1}</b>\n\n""".format(
                nombre, puntuacion(total_intercambios,
                    total_intercambios-puntos_negativos)
                )
        msg_response_cabecera += """Total Intercambios: <b>{0}</b>\n """.format(
                total_intercambios)

        msg_response_final = msg_response_cabecera + msg_response

    update.message.reply_text(parse_mode="html",
            text=emojize(msg_response_final, use_aliases=True))
    return True


def trade_califica(bot, update, args):
    chat_id = update.message.from_user.id

    def valida_permiso(cont, user):
        try:
            Contrato.objects.get(contrato=cont).contratos.get(
                            user__chat_id=user)
        except ObjectDoesNotExist:
            return False

        return True

    if len(args) >= 2:
        contrato_id = args[0]
        contrato_comentario = ' '.join(args[1:])

        if not valida_permiso(contrato_id, chat_id):
            msg_response = """
            :no_entry_sign: No eres usuario de este contrato: <b>{0}</b>
            """.format(contrato_id)

            update.message.reply_text(parse_mode="html",
                    text=emojize(msg_response, use_aliases=True))
            return False

        pos = "califica,pos,{0},{1}".format(contrato_id, contrato_comentario)
        neg = "califica,neg,{0},{1}".format(contrato_id, contrato_comentario)
        neu = "califica,neu,{0},{1}".format(contrato_id, contrato_comentario)

        keyboard = [[
                InlineKeyboardButton("Positivo", callback_data=pos),
                InlineKeyboardButton("Negativo", callback_data=neg),
                InlineKeyboardButton("Neutral", callback_data=neu),
                ]]
        reply_markup2 = InlineKeyboardMarkup(keyboard)

        try:
            usuario_contrato = Contrato.objects.get(
                    contrato=contrato_id).contratos.get(
                            ~Q(user__chat_id=chat_id))

            nombre = usuario_contrato.user.username if usuario_contrato.user.username \
                    else usuario_contrato.user.first_name

            update.message.reply_text('Califique a {0} como:'.format(nombre),
                    reply_markup=reply_markup2)
        except ObjectDoesNotExist:
            msg_response = """
            :no_entry_sign: No fue posible encontrar el contrato: <b>{0}</b>
            """.format(contrato_id)

            update.message.reply_text(parse_mode="html",
                    text=emojize(msg_response, use_aliases=True))
            return False
    else:
        msg_response = """
       :no_entry_sign: Debes indicar el
       numero de contrato
       y un comentario sobre
       la persona con la cual
       hiciste el contrato.\n
       :bulb: Ejemplo:
       <b>/tradec 1104 Todo bien</b>\n
       Ejecuta <b>/trade ?</b>
       para obtener mas ayuda
       """
        update.message.reply_text(parse_mode="html",
                text=emojize(msg_response, use_aliases=True))
    return True


def callback_califica(bot, update):
    query = update.callback_query
    metodo, feedback, contrato_id, contrato_comentario = query.data.split(',')
    id_evaluador = update.callback_query.from_user.id
    nombre_evaluador = update.callback_query.from_user.username if \
            update.callback_query.from_user.username else \
            update.callback_query.from_user.first_name

    try:

        # Usuario Evaludado
        usuario_evaluado = Contrato.objects.get(
                contrato=contrato_id).contratos.get(
                        ~Q(user__chat_id=id_evaluador))
        evaludado_chat_id = usuario_evaluado.user.chat_id

        nombre_evaluado = usuario_evaluado.user.username \
                if usuario_evaluado.user.username else \
                usuario_evaluado.user.first_name

        # Usuario Evaluador
        usuario_contrato = Contrato.objects.get(
                contrato=contrato_id).contratos.get(
                        user__chat_id=id_evaluador)

        usuario_contrato.comentario = contrato_comentario
        usuario_contrato.puntuacion = feedback
        usuario_contrato.save()
        nombre = usuario_contrato.user.username \
                if usuario_contrato.user.username else \
                usuario_contrato.user.first_name

        msg_response = """
        :sparkles: Calificacion realizada con exito, el usuario <b>{0}</b> tambien ha sido notificado""".format(nombre_evaluado)

        # Notificar al usuario que ha sido calificado
        if feedback == 'pos':
            emo = ":smiley:"
            cal = "Positivo"
        elif feedback == "neg":
            emo = ":rage:"
            cal = 'Negativo'
        elif feedback == "neu":
            emo = ":no_mouth:"
            cal = 'Neutral'

        msg_response2 = """
        :bell: El usuario <b>{1}</b> te ha calificado como: <b>{2}</b> {0}, No olvides calificarlo tu si aun no lo has hecho\nEjecuta /tradec {3} Tu comentario .
        """.format(emo, nombre_evaluador, cal, usuario_contrato.contrato)

        bot.sendMessage(evaludado_chat_id, parse_mode='html',
                text=emojize(msg_response2, use_aliases=True))

    except ObjectDoesNotExist:
        msg_response = """
        :no_entry_sign: No fue posible evaluar a la persona
        """.format(contrato_id)

    def cerrar_contrato(contrato_id):
        # TODO: Validar el tiempo  que ha transcurrido desde que se creo el
        # contrato para ver si se enviar el mensaje

        try:
            contrato = Contrato.objects.get(
                    contrato=contrato_id).contratos.filter(
                    comentario__isnull=False)

            if len(contrato) >=2:
                grupo_chat_id = contrato[0].contrato.grupo.grupo_id
                operacion = contrato[0].contrato.operacion
                user1 = contrato[0].user.username if contrato[0].user.username\
                        else contrato[0].user.first_name

                user2 = contrato[1].user.username if contrato[1].user.username\
                        else contrato[1].user.first_name
                calif1 = contrato[0].comentario
                calif2 = contrato[1].comentario

                msg_response3 = """:pushpin: Contrato finalizado\n\n:small_orange_diamond:<b>Contrato:</b><b>{0}</b>\n\n:small_orange_diamond:<b>Operacion:</b> {1}\n\n:small_orange_diamond:<b>#Ref:</b> @{2} fue calif. como {5}\n\n:small_orange_diamond:<b>#Ref:</b> @{4} fue calif. como {3}\n\n:bulb: <b>Tips:</b>\n\n- Si quieres saber mas acerca de la operacion puedes consultar el contrato con el siguiente comando:\n\n - Ejecuta:\n <b>/tradeb {0}</b>
                """.format(contrato_id, operacion, user1,
                        calif1, user2, calif2 )
                bot.sendMessage(grupo_chat_id, parse_mode="html",
                        text=emojize(msg_response3, use_aliases=True))

        except ObjectDoesNotExist:
            pass

    cerrar_contrato(contrato_id)

    query.edit_message_text(parse_mode="html", text=emojize(msg_response,
        use_aliases=True))


def crear_contrato(bot, update, args):

    import ipdb; ipdb.set_trace() # BREAKPOINT
    buyer_seller = []
    inf_operacion = []
    if args:
        inf_operacion.append(' '.join(args))
    else:
        inf_operacion = []

    if not inf_operacion:
        msg_response = ":no_entry_sign: Debes indicar el motivo de la operacion.\n<b>Ej: /trade venta de BTC por USD</b>\n Ejecuta <b>/trade ?</b> para obtener ayuda"
        update.message.reply_text(parse_mode="html",
                text=emojize(msg_response, use_aliases=True))
        return True

    elif inf_operacion[0] == '?':
        msg_response = ayuda_trade()
        update.message.reply_text(parse_mode="html",
                text=emojize(msg_response, use_aliases=True))
        return True

    keyboard = [[
            InlineKeyboardButton("Si", callback_data="contrato,aceptar"),
            InlineKeyboardButton("No", callback_data="contrato,cancelar")]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Desea crear un contrato de compra venta?:',
            reply_markup=reply_markup)
    return True


def callback_button(bot, update):
    query = update.callback_query

    metodo = query.data.split(',')
    if metodo[0] == 'contrato':
        opcion = metodo[1]
        if opcion == "aceptar":
            keyboard = [[InlineKeyboardButton("Soy el Vendedor",
                callback_data="contrato,vendedor"), ]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.edit_message_text('Presione este boton solo el <b>Vendedor</b>:',
                    parse_mode="html",  reply_markup=reply_markup)

        elif opcion == "vendedor":
            buyer_seller.append((query.from_user.username, query.from_user.id, 'Vendedor'))
            keyboard = [[InlineKeyboardButton("Soy el Comprador",
                callback_data="contrato,comprador"), ], ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            query.edit_message_text('Ahora presione este boton el <b>Comprador</b>:',
                    parse_mode="html", reply_markup=reply_markup)

        elif opcion == "comprador":
            buyer_seller.append((query.from_user.username, query.from_user.id, 'Comprador'))
            keyboard = [[
                InlineKeyboardButton("Generar", callback_data="contrato,generar"),
                InlineKeyboardButton("Cancelar", callback_data="contrato,cancelar_generar")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            query.edit_message_text('Presione para generar el contrato compra-venta:',
                    reply_markup=reply_markup)

        elif opcion == "generar":
            grupo_chat_id = query.message.chat.id
            grupo_chat_titulo = query.message.chat.title
            grupo_chat_tipo = query.message.chat.type
            contrato = Contrato.generar_nro_contrato()
            comprador = buyer_seller[1]
            vendedor = buyer_seller[0]

            msg_response = """
            :pushpin: <code>Se ha generado un contrato compra-venta:</code>\n\n<b>Contrato:</b><b>{0}</b>\n<b>Operacion:</b> {1}\n<b>Comprador:</b> {2}\n<b>vendedor:</b> {3}\n<b>Grupo:</b> {4}\n<b>Status:</b> En Proceso\n\n:bulb: <b>Tips</b>\n - Guarda el numero contrato\n - Ejecuta <b>/trade ? para ayuda</b>
            """.format(contrato, inf_operacion[0], comprador[0], vendedor[0],
                    grupo_chat_titulo)

            obj_grupo = Grupo.buscar_o_crear(grupo_chat_id, grupo_chat_titulo,
                    grupo_chat_tipo)
            try:
                obj_contrato = Contrato.objects.create(contrato=contrato,
                        grupo=obj_grupo, operacion=inf_operacion[0])
                for usuario in buyer_seller:
                    obj_user = User.objects.filter(chat_id=usuario[1])
                    if obj_user:
                        try:
                            PersonaContrato.objects.create(contrato=obj_contrato,
                                    user=obj_user[0], tipo_buyer_seller=usuario[2])
                        except Exception as e:
                            print(e)

            except Exception as e:
                msg_response = "Error al intentar crear el contrato"
            query.edit_message_text(parse_mode="html", text=emojize(msg_response,
                use_aliases=True))

        elif opcion == "contrato,cancelar_generar":
            query.edit_message_text('Cancelado')

        elif opcion == "contrato,cancelar":
            query.edit_message_text('Contrato cancelado:')

    elif metodo[0] == 'califica':
        callback_califica(bot, update)

    elif metodo[0] == 'alarma':
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

        opcion = metodo[1]
        if opcion == 'Activar':
            response = activar_desactivar('A')

        elif opcion == 'Desactivar':
            response = activar_desactivar('I')

        elif opcion == 'Ayuda':
            response = ayuda_set_alarma()

        elif opcion == 'Cancelar':
            response = "Comando cancelado"

        bot.edit_message_text(parse_mode="HTML", text=emojize(response, use_aliases=True),
                chat_id=query.message.chat_id,
                message_id=query.message.message_id)

    return True


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
    usuario = cadena_sin_el_comando.replace('@', '')

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
        bot.sendMessage(id_usuario_ban, parse_mode="Markdown", text=emojize(response, use_aliases=True))
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
    usuario = cadena_sin_el_comando.replace('@', '')

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
        bot.sendMessage(id_usuario_ban, parse_mode="Markdown", text=emojize(response, use_aliases=True))
        response = 'Usuario *{0}* expulsado :rocket: por _{1}_ :smiling_imp:'.format(username_usuario_ban, update.message.from_user.username)
    else:
        response = ':x: No fue posible expulsar el usuario {0} con el id {1}'.format(username_usuario_ban, id_usuario_ban)

    bot.sendMessage(update.message.chat_id, parse_mode="Markdown", text=emojize(response, use_aliases=True))
    return True


def unban(bot, update):
    parameters = update.message.text
    cadena_sin_el_comando = ' '.join(parameters.split()[1:])
    usuario = cadena_sin_el_comando.replace('@', '')
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
        response = ayuda_set_alarma()

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
    if not valida_autorizacion_comando(bot, update):
        bot.sendMessage(update.message.chat_id, text=emojize("comando desabilitado por el admin, :speaker: Intenta hacerlo en privado al bot", use_aliases=True))
        return True

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
        bot.sendMessage(update.message.chat_id, text=emojize("comando desabilitado por el admin, :speaker: Intenta hacerlo en privado al bot", use_aliases=True))
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
    if not valida_autorizacion_comando(bot, update):
        bot.sendMessage(update.message.chat_id, text=emojize("comando desabilitado por el admin, :speaker: Intenta hacerlo en privado al bot", use_aliases=True))
        return True

    print(update.message)
    parameters = update.message.text
    cadena_sin_el_comando = ' '.join(parameters.split()[1:])

    params = cadena_sin_el_comando.split() if \
            len(cadena_sin_el_comando.split()) in range(1, 3) else []

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
    if not valida_autorizacion_comando(bot, update):
        bot.sendMessage(update.message.chat_id, text=emojize("comando desabilitado por el admin, :speaker: Intenta hacerlo en privado al bot", use_aliases=True))
        return True
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
    implicito = float(rq.get("USD").get("efectivo"))
    dicom = float(rq.get("USD").get("sicad2"))
    cucuta = float(rq.get("USD").get("efectivo_cucuta"))
    localbitcoin = float(rq.get("USD").get("localbitcoin_ref"))
    barril = float(rq.get("MISC").get("petroleo").replace(",", "."))
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
    if not valida_autorizacion_comando(bot, update):
        bot.sendMessage(update.message.chat_id, text=emojize("comando desabilitado por el admin, :speaker: Intenta hacerlo en privado al bot", use_aliases=True))
        return True
 
    print(update.message)
    user_first_name = update.message.from_user.first_name
    bot.sendMessage(update.message.chat_id, parse_mode="Markdown", text=emojize(get_dolartoday2(),
        use_aliases=True)
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

    /trade - Crea un contrato compra venta
    /trade ? - Para obtener ayuda
    /tradec - Calificar Conrtato
    /tradeb - Buscar Inf Conrato
    /traderef - Referencias de usuario

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
        keyboard = [[InlineKeyboardButton("Activar", callback_data='alarma,Activar'),
                    InlineKeyboardButton("Desactivar", callback_data='alarma,Desactivar')],
                    [InlineKeyboardButton("Ayuda", callback_data='alarma,Ayuda'),
                    InlineKeyboardButton("Regresar", callback_data='alarma,Cancelar')]]

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
    m = evaluar(update.message.text)
    if m:
        update.message.reply_text(m)
    usuario_nuevo(update)


def unknown(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Lo siento, No reconozco ese comando.")


def main():
    logger.info("Loading handlers for telegram bot")

    # Default dispatcher (this is related to the first bot in settings.TELEGRAM_BOT_TOKENS)
    dp = DjangoTelegramBot.dispatcher
    # To get Dispatcher related to a specific bot
    # dp = DjangoTelegramBot.getDispatcher('BOT_n_username')  #get by bot username

    dp.add_handler(CommandHandler("trade2user", trade2user, pass_args=True))
    dp.add_handler(CommandHandler("traderef", trade_referencia, pass_args=True))
    dp.add_handler(CommandHandler("tradec", trade_califica, pass_args=True))
    # dp.add_handler(InlineQueryHandler(reply_to_query))

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("reglas", reglas))
    dp.add_handler(CommandHandler("ban", ban))
    dp.add_handler(CommandHandler("kick", kick))
    dp.add_handler(CommandHandler("unban", unban))

    dp.add_handler(CommandHandler("trade", crear_contrato, pass_args=True))
    dp.add_handler(CallbackQueryHandler(callback_button))

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

