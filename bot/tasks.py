# -*- encoding: utf-8 -*-
from selenium import webdriver
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

# from bot.telegrambot import get_dicom_gobierno, get_localbitcoin_precio, get_dolar_gobierno
from django.conf import settings
# celery -A pyloro worker -l info


from lib.airtm import AirTM

URL_AREPA_BTC_USD = settings.CRIPTO_MONEDAS.get("URL_AREPACOIN")
URL_WCC = settings.CRIPTO_MONEDAS.get("URL_WCC")
URL_RIL = settings.CRIPTO_MONEDAS.get("URL_RIL")
URL_PRICE_USD_EUR_MARKET = settings.CRIPTO_MONEDAS.get("URL_PRICE_USD_EUR_MARKET")
URL_DOLARTODAY = settings.CRIPTO_MONEDAS.get("URL_DOLARTODAY")

def get_price_usd_eur(coin_ticker, market='coinbase'):
    url = URL_PRICE_USD_EUR_MARKET.format(coin_ticker.upper())
    data = requests.get(url)
    response = data.json() if data else ''
    return response

def get_dolar_interbanex():
    vdisplay = Display(visible=0, size=(1024, 768))
    vdisplay.start()

    driver = webdriver.Firefox(firefox_profile='/usr/local/bin/')  # executable_path="/usr/local/bin/geckodriver")
    url = 'https://www.interbanex.com'
    ruta_xpath = "//*[contains(@class, 'value')]"
    driver.get(url)
    wait = WebDriverWait(driver, 3)
    monto = 0

    try:
        if driver.find_elements_by_xpath(ruta_xpath)[0]:
            monto = driver.find_elements_by_xpath(ruta_xpath)[0].text
            monto = monto.replace('Bs', '').replace('.', '').replace(',', '.').strip()
    except Exception as error:
        monto = 0
        print('Error al consultar interbanex', error)

    driver.close()
    vdisplay.stop()

    return float(monto)

def get_dolar_gobierno():
    dolar_gobierno = '0'
    URL = 'https://www.casadecambiozoom.com/'
    ruta ='/html/body/div[3]/div/div[2]/a/font'
    try:
        page = requests.get(URL, timeout=10)
        tree = html.fromstring(page.content)
        resultado_bs = tree.xpath(ruta)
    except:
        resultado_bs = 0

    if resultado_bs:
        try:
            print('aqui', resultado_bs[0].text)
            dolar_gobierno = resultado_bs[0].text.replace('Bs.S.', '').strip()
        except:
            dolar_gobierno = '0'
    return dolar_gobierno

def  get_dolar_interbanex():
    dolar_bolivar_interbanex = '0'
    URL = 'https://www.interbanex.com'
    ruta = '/html/body/app-root/app-login/div/div[1]/div[1]/div[1]/div[2]/div[2]/app-instrument/div/div/div[2]/div[3]/div[1]/span[2]'

    try:
        page = requests.get(URL, timeout=10)
        tree = html.fromstring(page.content)
        resultado_bs = tree.xpath(ruta)
    except:
        resultado_bs = 0

    if resultado_bs:
        try:
            print('BolivarInterbanex scrapy:', resultado_bs[0].text)
            dolar_bolivar_interbanex =  float(resultado_bs[0].text.replace('.', '').replace(',', '.').strip())
        except:
            dolar_bolivar_interbanex = 0
    return dolar_bolivar_interbanex

def  get_dolar_bolivar_cucuta():
    dolar_bolivar_cucuta = '0'
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


def api_tuiter():
    consumer_key = "wz6LRrWGEj0cfOsSqNKLg"
    consumer_secret = "JQUF9IFiFOpzjpTKYxsbKl5QV6o0baoD37fxFpBEE"
    access_token = "23130430-jfgPU8pnQks4AuW5XpS9Wfg3IaYMd4jB88zw8nPm4"
    access_token_secret = "8q9haKn2GrtqDmqMjxRCH0x8UEst1Ckt33AsnJYk"

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    return api


# @app.task
def get_price_from_twiter(nombre):

    def _validar_condicion(usuario_tuiter, status):
        if usuario_tuiter == 'theairtm':
            if 'tasa' in status.text.lower() and '#ven' in status.text.lower():
                return True
        elif usuario_tuiter == 'dolarprocom':
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
        stuff = tweepy.Cursor(api.user_timeline, screen_name=nombre, include_rts=True)
        return stuff

    def descargar_imagen(nombre, status):
        if _validar_condicion(nombre, status):
            response = ''
            media = status.entities.get('media')
            if media:
                url_imagen = media[0].get('media_url')
                if url_imagen:
                    ruta_imagen_tasa = 'graficos/tasa_{0}.jpg'.format(nombre)
                    # urllib2.urlretrieve(url_imagen, ruta_imagen_tasa)
                    response = ruta_imagen_tasa
            return response

    def get_tweets(stuff, n, nombre):
        for index, status in enumerate(stuff.items(n)):
            today = status.created_at.date()
            # response_ruta = descargar_imagen(nombre, status)
            # Por ahora se harcodea esta opcion, no recuerdo que funcion hacia
            # descargar imagen
            response_ruta = True
            texto = status.text

            #if response_ruta:
            if _validar_condicion(nombre, status):
                if today == datetime.now().date():
                    response = True, response_ruta, texto
                    break
                else:
                    response = False, response_ruta, texto
                    break
            else:
                response = False, '', 'No disponible'
        return response

    def parsear_tasa(texto):
        response = ''
        texto_descomponer = texto.split() if len(texto.split()) >= 3 else ''
        if texto_descomponer:
            tasa = [float(palabra.replace(',', '')) for palabra in texto.split() if len(palabra) > 3 and palabra.replace(',', '').replace('.', '').isdigit()]
            # tasa = texto_descomponer[0] if texto_descomponer[0].lower() == 'tasa' or texto_descomponer[0].upper() == u'ACTUALIZACIÓN' else ''
            # moneda = texto_descomponer[3] if texto_descomponer[3].lower() == 'bsf' else ''
            moneda = 'tasa' in texto.lower() and 'bs.s' in texto.lower() and '#ven' in texto.lower()
            if tasa and moneda:
                response = str(tasa[0])
        return response

    stuff = get_stuff(nombre)
    hoy, ruta_img, texto = get_tweets(stuff, 50, nombre)
    return parsear_tasa(texto)


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

def get_price_arepacoin2(dolartoday):
    precio_dtd = dolartoday if dolartoday else 0
    precio_airtm = float(get_price_from_twiter('theairtm').strip()) if \
            get_price_from_twiter('theairtm') else 0
    dolartoday if dolartoday else 0

    precio_usd_arepa = 0
    precio_vef_arepa = 0
    precio_btc_arepa = 0
    precio_vef_arepa_airtm = 0

    URL = "https://coinlib.io/coin/AREPA/ArepaCoin"

    page = requests.get(URL)
    tree = html.fromstring(page.content)
    resultado_usd = tree.xpath('//*[@id="coin-main-price"]')
    resultado_btc = tree.xpath('//*[@id="altprice-859"]')

    if resultado_btc:
        precio_btc_arepa = float(resultado_btc[0].text.replace('BTC', '').strip())

    if resultado_usd:
        precio_usd_arepa = float(resultado_usd[0].text.replace(u'\xa0', '').replace(u'\n', '').replace('$', ''))

    precio_vef_arepa = precio_usd_arepa * precio_dtd
    precio_vef_arepa_airtm = precio_usd_arepa * precio_airtm

    return precio_usd_arepa, precio_vef_arepa, precio_vef_arepa_airtm, precio_btc_arepa

def get_price_wcc(dolartoday):
    def get_price_usd_eur(coin_ticker, market='coinbase'):
        url = URL_PRICE_USD_EUR_MARKET.format(coin_ticker.upper())
        data = requests.get(url)
        response = data.json() if data else ''
        return response

    precio_dtd = dolartoday if dolartoday else 0
    precio_airtm = float(get_price_from_twiter('theairtm').strip()) if \
            get_price_from_twiter('theairtm') else 0
    dolartoday if dolartoday else 0

    precio_usd_wcc = 0
    precio_vef_wcc = 0
    precio_btc_wcc = 0
    precio_vef_wcc_airtm = 0

    rq = requests.get(URL_WCC).json()
    if rq.get('success'):
        precio_btc_wcc = float(rq.get('result').get('Last') if rq.get('result').get('Last') else '0')

    precio_usd_wcc = float(get_price_usd_eur("BTC", "bitfinex").get('USD')) * precio_btc_wcc
    precio_vef_wcc = precio_usd_wcc * precio_dtd
    precio_vef_wcc_airtm = precio_usd_wcc * precio_airtm

    return precio_usd_wcc, precio_vef_wcc, precio_vef_wcc_airtm, precio_btc_wcc

@app.task
def wolfclover(chat_id, dolartoday):
    precio_usd_arepa, precio_vef_arepa, precio_vef_arepa_airtm, precio_btc_arepa  = get_price_wcc(dolartoday)
    response = """El precio de WolfCloverCoin es:\n\n\U0001F1FB\U0001F1EA <b>VEF Dolartoday:</b> {0:,.2f}\n\U0001F1FB\U0001F1EA <b>VEF AirTM:</b> {2:,.2f}\n<b>:dollar: USD:</b> {1:,.8f}\n\u0243 <b>BTC</b> {3:,.8f}\n\n <b>Precios Basados en https://trade.thexchanger.io</b>""".format(precio_vef_arepa, precio_usd_arepa, precio_vef_arepa_airtm, precio_btc_arepa)
    DjangoTelegramBot.dispatcher.bot.sendMessage(chat_id, parse_mode="html", text=emojize(response, use_aliases=True))


def get_price_ril(dolartoday):
    def get_price_usd_eur(coin_ticker, market='coinbase'):
        url = URL_PRICE_USD_EUR_MARKET.format(coin_ticker.upper())
        data = requests.get(url)
        response = data.json() if data else ''
        return response

    precio_dtd = dolartoday if dolartoday else 0
    precio_airtm = float(get_price_from_twiter('theairtm').strip()) if \
            get_price_from_twiter('theairtm') else 0
    dolartoday if dolartoday else 0

    precio_usd_ril = 0
    precio_vef_ril = 0
    precio_btc_ril = 0
    precio_vef_ril_airtm = 0

    rq = requests.get(URL_RIL).json()
    if rq:
        if rq[0].get('instrument'):
            precio_btc_ril = float(rq[0].get('last') if rq[0].get('last') else '0')

    precio_usd_ril = float(get_price_usd_eur("BTC", "bitfinex").get('USD')) * precio_btc_ril
    precio_vef_ril = precio_usd_ril * precio_dtd
    precio_vef_ril_airtm = precio_usd_ril * precio_airtm

    return precio_usd_ril, precio_vef_ril, precio_vef_ril_airtm, precio_btc_ril

@app.task
def rilcoin(chat_id, dolartoday):
    precio_usd_ril, precio_vef_ril, precio_vef_ril_airtm, precio_btc_ril  = get_price_ril(dolartoday)

    response = """El precio de RilCoin es:\n\n\U0001F1FB\U0001F1EA <b>VEF Dolartoday:</b> {0:,.2f}\n\U0001F1FB\U0001F1EA <b>VEF AirTM:</b> {2:,.2f}\n<b>:dollar: USD:</b> {1:,.8f}\n\u0243 <b>BTC</b> {3:,.8f}\n""".format(precio_vef_ril, precio_usd_ril, precio_vef_ril_airtm, precio_btc_ril)

    DjangoTelegramBot.dispatcher.bot.sendMessage(chat_id, parse_mode="html", text=emojize(response, use_aliases=True))

def get_price_arepacoin(dolartoday):
    precio_dtd = dolartoday if dolartoday else 0
    precio_airtm = float(get_price_from_twiter('theairtm').strip()) if \
            get_price_from_twiter('theairtm') else 0
    dolartoday if dolartoday else 0

    precio_usd_arepa = 0
    precio_vef_arepa = 0
    precio_btc_arepa = 0
    precio_vef_arepa_airtm = 0

    coincap_data = requests.get(URL_AREPA_BTC_USD).json()
    # coincap_json = coincap_data.get('data') if \
    #        coincap_data.get('status') == 'success' else {}

    coincap_json = coincap_data[0] if coincap_data else {}

    # arepa_values = [coin for coin in coincap_json \
    #        if coin.get('name').lower() == 'arepacoin'][0]

    if coincap_json:
        try:
            precio_btc_arepa = float(coincap_json.get('price_btc')) if coincap_json.get('price_btc') else 0
            precio_usd_arepa = float(coincap_json.get('price_usd')) if coincap_json.get('price_usd') else 0
        except:
            pass

    precio_vef_arepa = precio_usd_arepa * precio_dtd
    precio_vef_arepa_airtm = precio_usd_arepa * precio_airtm

    return precio_usd_arepa, precio_vef_arepa, precio_vef_arepa_airtm, precio_btc_arepa

@app.task
def arepacoin(chat_id, dolartoday):
    precio_usd_arepa, precio_vef_arepa, precio_vef_arepa_airtm, precio_btc_arepa  = get_price_arepacoin(dolartoday)

    response = """El precio de ArepaCoin es:\n\n\U0001F1FB\U0001F1EA <b>VEF Dolartoday:</b> {0:,.2f}\n\U0001F1FB\U0001F1EA <b>VEF AirTM:</b> {2:,.2f}\n<b>:dollar: USD:</b> {1:,.8f}\n\u0243 <b>BTC</b> {3:,.8f}\n""".format(precio_vef_arepa, precio_usd_arepa, precio_vef_arepa_airtm, precio_btc_arepa)

    DjangoTelegramBot.dispatcher.bot.sendMessage(chat_id, parse_mode="html", text=emojize(response, use_aliases=True))

def get_dolartoday_parse():
    rq = requests.get(URL_DOLARTODAY)  # .json()

    # USD
    dolartoday = float(rq.json().get('USD').get('transferencia'))
    dolartoday_btc = float(rq.json().get('USD').get('bitcoin_ref'))
    dolar_interbanex = 0  # get_dolar_interbanex()

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
    precio_airtm = get_price_from_twiter('theairtm').strip() if get_price_from_twiter('theairtm').strip() else 0
    precio_dolar_bolivar_cucuta = get_dolar_bolivar_cucuta()
    precio_dolar_gobierno = dicom  #  get_dolar_gobierno()

    # dolar_suma = dolartoday + dolartoday_btc + float(precio_airtm) + precio_dolar_bolivar_cucuta
    dolar_suma = dolartoday + dolartoday_btc + localbitcoin + float(precio_airtm) + precio_dolar_bolivar_cucuta + dolar_interbanex
    cantidad_a_promediar = len([f for f in (dolartoday, dolartoday_btc, localbitcoin, float(precio_airtm), precio_dolar_bolivar_cucuta, dolar_interbanex) if f])
    dolar_promedio = dolar_suma / cantidad_a_promediar
    print('Dolar promedio', dolar_promedio)

    response = """:speaker: DecimeMijoBot USD/EUR: {0}:\n\n\
    {14} <b>Casas Cambio</b>: {17}\n\
    {14} <b>DolarToday</b>: {1:0,.2f}\n\
    {14} <b>DT Bitcoin</b>: {18:0,.2f}\n\
    {14} <b>Dolar LBTC</b>: {5:0,.2f}\n\
    {14} <b>Dolar AirTM</b>: {15:0,.2f}\n\
    {14} <b>Dolar BolivarCucuta</b>: {19:0,.2f}\n\n\
    :euro: <b>DolarToday</b>: {6:0,.2f}\n\
    :euro: <b>Dicom</b>: {8:0,.2f}\n\
    {12} <b>RUB Bs</b>: {13:0,.2f}\n\n\
    {16} <b>Petroleo</b> USD: {10:0,.2f}\n\
    :moneybag: <b>Oro</b> USD: {11:0,.2f}\n\n\
    {14} <b>Bs Dolar Promedio</b>: {20:0,.2f}\n\n\
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
                    float(precio_airtm) if precio_airtm else 0,
                    emoji_barril,
                    precio_dolar_gobierno,
                    dolartoday_btc,
                    precio_dolar_bolivar_cucuta,
                    dolar_promedio,
                    dolar_interbanex
                    )

    return response

@app.task
def get_dolartoday_comando(chat_id):

    DjangoTelegramBot.dispatcher.bot.sendMessage(chat_id,
            parse_mode="html",
            text=emojize(get_dolartoday_parse(), use_aliases=True)
            )
