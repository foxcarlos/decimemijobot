import os
from time import sleep

while True:
    print("Ejecutando Alarma bitcoin")
    comando = "python /home/foxcarlos/desarrollo/python/decimemijobot/manage.py alerta_bitcoin bitcoin"
    os.system(comando)
    sleep(30)
    print("Ejecutando Alarma dolartoday")
    comando2 = "python /home/foxcarlos/desarrollo/python/decimemijobot/manage.py alerta_bitcoin dolartoday"
    os.system(comando2)
    sleep(30)
    print("Ejecutando Alarma Ethereum")
    comando3 = "python /home/foxcarlos/desarrollo/python/decimemijobot/manage.py alerta_bitcoin ethereum"
    os.system(comando3)
    sleep(30)
    print("Ejecutando Alarma LiteCoin")
    comando4 = "python /home/foxcarlos/desarrollo/python/decimemijobot/manage.py alerta_bitcoin litecoin"
    os.system(comando4)
    sleep(30)

