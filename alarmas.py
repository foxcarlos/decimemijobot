# from django.conf import settings
from sampleproject import settings

import os
from time import sleep



while True:
    base = settings.BASE_DIR
    django_mng = os.path.join(base, "manage.py")

    print("Ejecutando Alarma bitcoin")
    comando = "python {} alerta_bitcoin bitcoin".format(django_mng)
    try:
        os.system(comando)
    except Exceptions as e:
        pass
    sleep(30)
    print("Ejecutando Alarma dolartoday")
    comando2 = "python {0} alerta_bitcoin dolartoday".format(django_mng)
    os.system(comando2)
    sleep(30)
    print("Ejecutando Alarma Ethereum")
    comando3 = "python {0} alerta_bitcoin ethereum".format(django_mng)
    os.system(comando3)
    sleep(30)
    print("Ejecutando Alarma LiteCoin")
    comando4 = "python {0} alerta_bitcoin litecoin".format(django_mng)
    os.system(comando4)
    sleep(30)

