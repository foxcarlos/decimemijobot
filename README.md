# FoxBot Bot para Telegram
Bot Telegram funciones varias

Estas son las funciones que realiza el Bot

  - autor - Acerca de
  - donar - Si deseas hacer una donacion
  - help - Lista de comandos disponibles
  - bitcoin - Precio Bitcoin
  - dolartoday - Precio del Dolar Venezuela
  - allcoins - Precio de algunas las cripto monedas
  - precio - <coin_ticker> <Market> Ej: /precio btc coinbase
  - grafico - <coin_ticker> <market>
  - clc - <coin_ticker> <monto> - Calcula el valor del BTC de un monto of coin pasado
  - ban - banear un usuario del grupo
  - set_alarma_bitcoin - <estado> Ej: /set_alarma_bitcoin on
  - set_alarma_dolartoday - <estado> Ej: /set_alarma_bitcoin on
  - set_alarma_ethereum - <estado> Ej: /set_alarma_ethereum on
  - set_alarma_litecoin - <estado> Ej: /set_alarma_litecoin on
  - ban - reply al usuario y esribir /ban
  - trade - Crear un contrato compra venta
  - tradeb - Buscar Inf Conrato
  - tradec - Calificar Conrtato
  - traderef - Buscar Referencias de usuario
  
  
### Installation

FoxBot requires python v3+ to run.
```sh
$ sudo apt-get install python3 python3-doc
$ sudo apt-get install redis-server
```

= Repo =
```sh
$ git clone git@github.com:foxcarlos/foxbot.git
```
= Prepare Virtual Env =
```sh
$ mkdir ~/Envs
$ sudo pip install virtualenvwrapper
$ sudo apt-get install python-virtualenv

Note:Edit File in your Home
$ vim ~.bashrc
export WORKON_HOME=~/Envs
source /usr/local/bin/virtualenvwrapper.sh

Run in terminal
$ mkvirtualenv --python=/usr/bin/python3 foxbot
```
#### For telegrambot
```sh
$ pip install pyTelegramBotAPI

Or 

$ git clone https://github.com/eternnoir/pyTelegramBotAPI.git
$ cd pyTelegramBotAPI
$ python setup.py install
```

= Install the dependencies =
```sh
$ pip install -r requirements.txt
```

#### Run BOT

```sh
$ python manage.py botpolling --username=DecimeMijobot
```

#### Run Alertas from Crontab

```sh
python /home/foxcarlos/desarrollo/python/decimemijobot/manage.py alerta_bitcoin dolartoday
python /home/foxcarlos/desarrollo/python/decimemijobot/manage.py alerta_bitcoin bitcoin
```

#### Run Celery Workers
```sh
$ python manage.py celery worker -A sampleproject.celery --loglevel=info
```

### Notas:

 - Lista de nombre de emojis https://www.webpagefx.com/tools/emoji-cheat-sheet/

### readme.md Creado con https://dillinger.io/
