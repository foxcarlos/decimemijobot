from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from pyvirtualdisplay import Display

import requests
from lxml import html
from time import sleep
from pytube import YouTube
import os
from datetime import datetime
import urllib.request as urllib2
import urllib
from emoji import emojize
from bs4 import BeautifulSoup
import tweepy

from django_telegrambot.apps import DjangoTelegramBot
from sampleproject.celery import app

from django.conf import settings
# celery -A pyloro worker -l info


from lib.airtm import AirTM

URL_PRICE_USD_EUR_MARKET = settings.CRIPTO_MONEDAS.get("URL_PRICE_USD_EUR_MARKET")
URL_DOLARTODAY = settings.CRIPTO_MONEDAS.get("URL_DOLARTODAY")


def get_price_yadio():
    response = 0
    try:
        url = 'https://api.yadio.io/json'
        ok = requests.get(url)
    except Exception as e:
        ok = False

    try:
        response = ok.json().get('USD').get('rate')
        response = float(response)
    except Exception as e:
        response = 0
    return response
    
def get_price_usd_eur(coin_ticker, market='coinbase'):
    url = URL_PRICE_USD_EUR_MARKET.format(coin_ticker.upper())
    data = requests.get(url)
    response = data.json() if data else ''
    return response

def get_dolar_airtm():
    dolar_airtm = 0
    URL = 'https://rates.airtm.com/'
    ruta ='/html/body/div[1]/div[1]/div[4]/div[1]/div/span'
    try:
        page = requests.get(URL, timeout=10)
        tree = html.fromstring(page.content)
        resultado_bs = tree.xpath(ruta)
    except:
        resultado_bs = 0

    if resultado_bs:
        try:
            print('aqui', resultado_bs[0].text)
            dolar_airtm = float(resultado_bs[0].text.strip())
        except:
            dolar_airtm = 0
    return dolar_airtm

def get_dolar_gobierno():

    try:
       rq = requests.get(URL_DOLARTODAY)
       resultado_bs = float(rq.json().get("USD").get("sicad2"))
    except:
        resultado_bs = 0

    return resultado_bs

def  get_dolar_bolivar_cucuta():
    dolar_bolivar_cucuta = 0
    URL = 'http://bolivarcucuta.com/'
    ruta = '//*[@id="dolar"]'

    try:
        page = requests.get(URL, timeout=10)
        tree = html.fromstring(page.content)
        resultado_bs = tree.xpath(ruta)
    except:
        resultado_bs = 0

    if resultado_bs:
        try:
            print('BolivarCucuta scrapy:', resultado_bs[0].text)
            dolar_bolivar_cucuta =  float(resultado_bs[0].text.replace('BsF', '').replace(',', '').strip())
        except:
            dolar_bolivar_cucuta = 0
    return dolar_bolivar_cucuta

def get_rublo_precio(coin_ticker):
    # 26 Ene 2019
    data = get_price_usd_eur("USD", 'coinbase')
    monto = data.get('VES') / data.get(coin_ticker.upper())

def get_localbitcoin_precio(coin_ticker=''):
    # 26 Ene 2019
    # data = get_price_usd_eur("USD", 'coinbase')
    # monto = data.get('VES') / data.get(coin_ticker.upper())

    monto= 0
    url = 'https://localbitcoins.com/bitcoinaverage/ticker-all-currencies/'
    get_todas_las_monedas = requests.get(url)
    if get_todas_las_monedas.status_code == 200:
        try:
            todas_las_monedas = get_todas_las_monedas.json()
            info_usd = todas_las_monedas.get('USD')
            info_ves = todas_las_monedas.get('VES')

            promedio_usd_1h = info_usd.get('avg_1h')
            promedio_usd_12 = info_usd.get('avg_12h')

            promedio_ves_1h = info_ves.get('avg_1h')
            promedio_ves_12 = info_ves.get('avg_12h')

            monto_usd = promedio_usd_1h if promedio_usd_1h else promedio_usd_12
            monto_ves = promedio_ves_1h if promedio_ves_1h else promedio_ves_12
            monto = float(monto_ves) / float(monto_usd)

        except Exception as errorGet:
            monto = 0
            print('Error al calcular precio del localbitcoin', errorGet)

    return monto

def get_dicom_gobierno():
    eur_dicom_gobierno = '0'
    resultado_eur = ''
    URL = 'https://www.dicom.gob.ve/'
    ruta ='//*[@class="moneda moneda-eur even last"]//p[@class="value"]'
    try:
        page = requests.get(URL)
        tree = html.fromstring(page.content)
        resultado_eur = tree.xpath(ruta)
    except:
        pass

    if resultado_eur:
        eur_dicom_gobierno = resultado_eur[0].text.replace('.', '').replace(',', '.')
    return eur_dicom_gobierno

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


def yt2mp3_download(chat_id, url):
    import youtube_dl
    ydl_opts = {
            'format': 'worstaudio[ext=mp3]/worst',
            'outtmpl': '%(id)s',
            'noplaylist' : True,}

    ydl = youtube_dl.YoutubeDL(ydl_opts)
    descargar_archivo = ydl.extract_info(url)

    if descargar_archivo.get('id'):
        archivo = os.path.join(settings.BASE_DIR,
                '{0}'.format(descargar_archivo.get('id')))
        return archivo

    return False

def yt2mp3_convert(archivo):
    comando = 'ffmpeg -i "{0}" -vn -ar 44100 -ac 2 -ab 56k -f mp3 {1}'.format(
    archivo, archivo + '.mp3')
    print(comando)
    os.system(comando)
    return True

@app.task
def yt2mp3(chat_id, url):
    try:
        archivo = yt2mp3_download('', url)
        archivo_mp3 = yt2mp3_convert(archivo)

        print(archivo)
        file_ = open("{0}".format(archivo + '.mp3'), "rb")
        DjangoTelegramBot.dispatcher.bot.sendAudio(chat_id,
                audio=file_, caption=archivo, timeout=1000)

        file_.close()
        os.remove(archivo)
        os.remove(archivo + '.mp3')
    except Exception as E:
        print(E)

@app.task
def airtm_dolar_vef(chat_id):
    # instancia = AirTM()

    if not instancia.verificar_instancia_abierta():
        instancia.abrir_navegador()

    instancia.verfifica_login()
    sleep(5)
    dolar_airtm = instancia.obtener_precio()
    instancia.cerrar()
    print(dolar_airtm)

    if dolar_airtm:
        response = """El precio del Dolar AirTM es:\n\n\U0001F1FB\U0001F1EA <b>VEF:</b> {0:,.2f}""".format(dolar_airtm)
    else:
        response = ':x: <b>Error al consultar AirTM</b>'
    DjangoTelegramBot.dispatcher.bot.sendMessage(chat_id, parse_mode="html", text=emojize(response, use_aliases=True))

def get_dolartoday_parse():
    rq = requests.get(URL_DOLARTODAY)  # .json()

    # USD
    dolartoday = float(rq.json().get('USD').get('transferencia'))
    dolartoday_btc = float(rq.json().get('USD').get('bitcoin_ref'))
    dolar_efectivo = dolartoday + 2600  # get_dolar_interbanex()

    # implicito = float(rq.json().get("USD").get("efectivo"))
    implicito = float(rq.json().get("USD").get("efectivo_real"))
    dicom = float(rq.json().get("USD").get("sicad2"))
    cucuta = float(rq.json().get("USD").get("efectivo_cucuta"))
    barril = float(rq.json().get("MISC").get("petroleo").replace(",", "."))
    oro = float(rq.json().get("GOLD").get("rate"))
    fecha = datetime.now().strftime("%d-%m-%Y")

    # EUR
    dolartoday_e = float(rq.json().get('EUR').get('transferencia'))
    # implicito_e = float(rq.json().get("EUR").get("efectivo"))
    implicito_e = float(rq.json().get("EUR").get("efectivo_real"))
    dicom_e = float(get_dicom_gobierno())  # float(rq.json().get("EUR").get("sicad2"))
    cucuta_e = float(rq.json().get("EUR").get("efectivo_cucuta"))
    emoji_barril = u'\U0001F6E2'

    # LocalBitcoin
    # https://min-api.cryptocompare.com/data/price?fsym=USD&tsyms=VEF
    localbitcoin = get_localbitcoin_precio()

    # RUB
    rublo_vef = 0  # get_rublo_precio("RUB")

    emoji_bandera_rusa = u'\U0001F1F7\U0001F1FA'
    emoji_bandera_vzla = u'\U0001F1FB\U0001F1EA'
    datm = get_dolar_airtm()
    precio_airtm = datm if datm else 0
    precio_dolar_bolivar_cucuta = get_dolar_bolivar_cucuta()
    precio_dolar_yadio = get_price_yadio()
    precio_dolar_gobierno = dicom  #  get_dolar_gobierno()

    # dolar_suma = dolartoday + dolartoday_btc + float(precio_airtm) + precio_dolar_bolivar_cucuta
    dolar_suma = dolartoday + dolartoday_btc + localbitcoin + precio_airtm + precio_dolar_bolivar_cucuta + dolar_efectivo + precio_dolar_yadio
    cantidad_a_promediar = len([f for f in (dolartoday, dolartoday_btc, localbitcoin, precio_airtm, precio_dolar_bolivar_cucuta, dolar_efectivo, precio_dolar_yadio) if f])
    dolar_promedio = dolar_suma / cantidad_a_promediar
    print('Dolar promedio', dolar_promedio)

    response = """:speaker: DecimeMijoBot USD/EUR: {0}:\n\n\
    {14} <b>Casas Cambio</b>: {17}\n\
    {14} <b>DolarToday</b>: {1:0,.2f}\n\
    {14} <b>DT Bitcoin</b>: {18:0,.2f}\n\
    {14} <b>Localbitcoin</b>: {5:0,.2f}\n\
    {14} <b>AirTM</b>: {15:0,.2f}\n\
    {14} <b>BolivarCucuta</b>: {19:0,.2f}\n\
    {14} <b>Yadio</b>: {20:0,.2f}\n\
    {14} <b>Dolar Efectivo</b>: {22:0,.2f}\n\n\
    :euro: <b>DolarToday</b>: {6:0,.2f}\n\
    :euro: <b>Dicom</b>: {8:0,.2f}\n\
    {12} <b>RUB Bs</b>: {13:0,.2f}\n\n\
    {16} <b>Petroleo</b> USD: {10:0,.2f}\n\
    :moneybag: <b>Oro</b> USD: {11:0,.2f}\n\n\
    {14} <b>Bs Dolar Promedio</b>: {21:0,.2f}\n\n\
    Seguime en Twiter: https://twitter.com/decimemijobot\n\
        """.format(fecha,
                    dolartoday,
                    implicito,
                    dicom,
                    cucuta,
                    localbitcoin,
                    dolartoday_e,
                    implicito_e,
                    dicom_e,
                    cucuta_e,
                    barril,
                    oro,
                    emoji_bandera_rusa,
                    rublo_vef,
                    emoji_bandera_vzla,
                    precio_airtm,
                    emoji_barril,
                    precio_dolar_gobierno,
                    dolartoday_btc,
                    precio_dolar_bolivar_cucuta,
                    precio_dolar_yadio,
                    dolar_promedio,
                    dolar_efectivo
                    )

    return response

@app.task
def get_dolartoday_comando(chat_id):

    DjangoTelegramBot.dispatcher.bot.sendMessage(chat_id,
            parse_mode="html",
            text=emojize(get_dolartoday_parse(), use_aliases=True)
            )
