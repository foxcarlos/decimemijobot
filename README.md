# Bot FoxBOT

  - Usa Celery y Redis para ejecutar procesos en background para AFIP
  

### Installation

pyLoro requires python v3 to run.
```sh
$ sudo apt-get install python3.6 python3.6-doc
```

### Installation Redis Server

```sh
$ sudo aptitude install redis-server

### Test Redis server
$ redis-cli ping
```

= Repo =
```sh
$ git clone https://github.com/foxcarlos/foxbot.git
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
$ mkvirtualenv --python=/usr/bin/python3 para_python3
$ mkvirtualenv para_python2
```
#### For webscrapy Selenium and firefox download geckodriver
- Download https://github.com/mozilla/geckodriver/releases
- unzip file geckodriver
- copy file in /usr/local/bin/

= Install the dependencies =
```sh
$ pip install -r requirements.txt
```

### Todos

 - Write MORE Tests
 - Add Night Mode

### readme.md Creado con https://dillinger.io/
