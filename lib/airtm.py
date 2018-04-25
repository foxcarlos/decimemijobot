# -*- encoding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from datetime import datetime
import time
import logging


class AirTM(object):
    def __init__(self):
        '''.'''

        self.driver = webdriver.Firefox(executable_path="/usr/local/bin/geckodriver")
        url = 'https://www.airtm.io/email-prompt'
        self.driver.get(url)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        # create a file handler
        handler = logging.FileHandler('airtm.log')
        handler.setLevel(logging.INFO)

        # create a logging format
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        # add the handlers to the logger
        self.logger.addHandler(handler)
        time.sleep(10)

    def verfifica_login(self):
        '''.'''

        try:
            if self.driver.find_element_by_class_name("dropdown-toggle ng-binding header-no-rating-content-username").text != "CARLOS GARCIA":
                self.login()
        except Exception as e:
            print(e)
            self.ocurrio_una_excepcion(e)
            self.login()

    def login(self):
        '''.'''

        url_login = "https://auth.airtm.io/authorize/421d54fbe759b5c30fee920c19a5428987c024f8?response_type=token&client_id=421d54fbe759b5c30fee920c19a5428987c024f8&redirect_uri=https%3A%2F%2Fwww.airtm.io%2Fdashboard%2Fnew-setup&scope=user:read,cards:read,cards:write,transactions:write&pfEmail=foxcarlos@gmail.com&state=49c2d1d7-b0ad-4ad4-a3e0-89a282e7cbe4"
        usuario = self.driver.find_element_by_name("emailField")
        usuario.send_keys('garciadiazca@gmail.com')
        usuario.send_keys(Keys.RETURN)

        time.sleep(10)

        clave = self.driver.find_element_by_id("password")
        clave.send_keys('clipper56!?16')
        clave.send_keys(Keys.RETURN)
        time.sleep(10)

    def obtener_precio(self):
        dolar_airtm = 0
        clase_a_buscar = "header-ticker"
        precio = self.driver.find_element_by_class_name(clase_a_buscar).text
        if precio:
            get_vef = precio.split(" ")[-2]
            try:
                dolar_airtm = float(get_vef)
            except Exception as e:
                self.ocurrio_una_excepcion(e)
        self.cerrar()
        return dolar_airtm

    def ocurrio_una_excepcion(self, error):
        '''.'''

        self.logger.error(error, exc_info=True)
        self.cerrar()

    def cerrar(self):
        '''.'''
        self.driver.close()
