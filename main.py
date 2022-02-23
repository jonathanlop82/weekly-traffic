import pysftp
import os
import csv
from datetime import datetime, timedelta
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np


HOSTNAME = "data.shoppertrak.com"
USERNAME = "altaplaza"
PASSWORD = os.environ.get("FTP_CREDENTIALS_SHOPPERTRAK")

NAMES_DAYS = ['Lunes','Martes','Miercoles','Jueves', 'Viernes', 'Sabado','Domingo']

today = datetime.now().strftime("%Y%m%d")
#yesterday = (today - timedelta(days=1)).strftime("%Y-%m-%d")
#today = input("Fecha: ")


class My_Connection(pysftp.Connection):
    def __init__(self, *args, **kwargs):
        self._sftp_live = False
        self._transport = None
        super().__init__(*args, **kwargs)

cnopts = pysftp.CnOpts()
cnopts.hostkeys = None

### Check if file exist and copy if not exist
with My_Connection(host=HOSTNAME, username=USERNAME, password=PASSWORD, cnopts=cnopts) as srv:

    data = srv.listdir()
    for file in data:
        f = Path(f"files/{file}")
        if f.is_file():
            pass
        else:
            srv.get(remotepath=file, localpath=f'./files/{file}')


def read_one_file(day):
    traffic = 0
    with open(f'./files/Extract_{day}.csv', 'r') as datafile:
            csv_file = csv.reader(datafile)

            for row in csv_file:
                #print(row[5])
                id,place,door,date,hour,traffic_count,traffic_es,letter = row
                #print(door)
                traffic += int(traffic_count)

    return traffic

def autolabel(rects):
    """Funcion para agregar una etiqueta con el valor en cada barra"""
    for rect in rects:
        height = rect.get_height()
        ax.annotate('{}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')

#read_one_file(day)

trafico = []
## retornar dias de la semana
weekday = (datetime.now() - timedelta(days=(1))).weekday()
print(weekday)
for i in range(7):
    print(NAMES_DAYS[i],end=" - ")
    if i - weekday <= 0:
        day = (datetime.now() - timedelta(days=(weekday - i))).strftime("%Y%m%d")
        print(f'{(datetime.now() - timedelta(days=(weekday - i +1))).strftime("%d-%m-%Y")}',end=" ")
        print(f'Trafico: {read_one_file(day)}')
        trafico.append(read_one_file(day))
    elif i - weekday > 0:
        print(f'{(datetime.now() + timedelta(days=(i - weekday - 1))).strftime("%d-%m-%Y")}')
        trafico.append(0)



fig, ax = plt.subplots()
ax.set_title('Tráfico Semanal')
#Colocamos una etiqueta en el eje Y
ax.set_ylabel('Tráfico')
#Colocamos una etiqueta en el eje X
ax.set_xlabel('Día')
#Creamos la grafica de barras utilizando 'dias' como eje X y 'trafico' como eje y.
bar = plt.bar(NAMES_DAYS, trafico)
autolabel(bar)
plt.savefig('trafico-semanal.png')
#Finalmente mostramos la grafica con el metodo show()
plt.show()




