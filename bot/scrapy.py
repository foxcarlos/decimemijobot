# -*- encoding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from datetime import datetime
import time
import logging


class NoticiasPanorama(object):

    def __init__(self):
        '''.'''

        self.driver = webdriver.Firefox(executable_path="/usr/local/bin/geckodriver")
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        # create a file handler
        handler = logging.FileHandler('panorama.log')
        handler.setLevel(logging.INFO)

        # create a logging format
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        # add the handlers to the logger
        self.logger.addHandler(handler)


    def cerrar(self):
        '''.'''

        self.driver.close()

    def sucesos(self):
        '''.'''

        url = 'http://www.panorama.com.ve/seccion/sucesos.html'
        ruta_xpath = '//div[@class="col1-sec"]/section/article[@class="nota_tipo2_box"]/div[@class="texto_tipo2"]/div[@class="titular_tipo2"]/a'
        titulares = ''

        self.driver.get(url)
        wait = WebDriverWait(self.driver, 10)
        time.sleep(6)

        for titular in self.driver.find_elements_by_xpath(ruta_xpath):
            titulares+="- {0}\n\n".format(titular.get_property("href"))

        self.cerrar()
        return titulares
