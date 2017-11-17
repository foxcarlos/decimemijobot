# -*- encoding: utf-8 -*-

from sampleproject.celery import app
from time import sleep

# celery -A pyloro worker -l info

@app.task
def prueba_suma(x, y):
    """."""

    # Se fuerza la tarea a  una espera solo para probar la sincronicidad
    sleep(6)
    print("Entro")
    print(self.xx)
    return x * y

@app.task
def prueba_resta(self, x, y):
    """."""
    return x - y
