# DecimeMijo Bot para Telegram
Bot Telegram funciones varias

Estas son las funciones que realiza el Bot

  - Hola
  - Chao
  

### Installation

DecimeMijo requires python v3+ to run.
```sh
$ sudo apt-get install python3 python3-doc
```

= Repo =
```sh
$ git clone git@github.com:foxcarlos/decimemijobot.git
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
$ mkvirtualenv --python=/usr/bin/python3 decimemijobot
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

python /home/foxcarlos/desarrollo/python/decimemijobot/manage.py alerta_bitcoin dolartoday
python /home/foxcarlos/desarrollo/python/decimemijobot/manage.py alerta_bitcoin bitcoin

### Todos

 - Write MORE Tests
 - Add Night Mode

### readme.md Creado con https://dillinger.io/
