import pysftp
import os
import csv
from datetime import datetime, timedelta
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
import smtplib


HOSTNAME = "data.shoppertrak.com"
USERNAME = "altaplaza"
PASSWORD = "mZZyG9NFWLu*JG"

NAMES_DAYS = ['Lunes','Martes','Miercoles','Jueves', 'Viernes', 'Sabado','Domingo']


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


def send_email(message):

    # assign key email aspects to variables for easier future editing
    subject = "Trafico diario de visitantes"
    body = message
    sender_email = "bot@altaplazamall.com"
    receiver_email = "soporte@altaplazamall.com"
    email=MIMEMultipart()
    email["From"] = sender_email
    email["To"] = receiver_email 
    email["Subject"] = subject
    email.attach(MIMEText(body, "plain"))
    image = MIMEImage(open('trafico-semanal.png', 'rb').read())
    image.add_header('Content-ID', '<image1>')
    email.attach(image)
    report = MIMEBase("application", "octate-stream")
    session = smtplib.SMTP('smtp-relay.gmail.com', 587) #use gmail with port
    session.starttls() #enable security
    text = email.as_string()
    session.sendmail(sender_email, receiver_email, text)
    session.quit()
    print('Mail Sent')

#read_one_file(day)

trafico = []
trafico_semana_anterior = []
## retornar dias de la semana
weekday = (datetime.now() - timedelta(days=(1))).weekday()
for i in range(7):
    if i - weekday <= 0:
        day = (datetime.now() - timedelta(days=(weekday - i))).strftime("%Y%m%d")
        previous_day = (datetime.now() - timedelta(days=(weekday - i + 7))).strftime("%Y%m%d")
        trafico.append(read_one_file(day))
        trafico_semana_anterior.append(read_one_file(previous_day))
        if i - weekday == 0:
            trafico_ayer = read_one_file(day)
    elif i - weekday > 0:
        previous_day = (datetime.now() - timedelta(days=(7 - i + weekday))).strftime("%Y%m%d")
        trafico.append(0)
        trafico_semana_anterior.append(read_one_file(previous_day))


'''

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
#plt.show()

'''

print(trafico)
print(trafico_semana_anterior)


#Obtenemos la posicion de cada etiqueta en el eje de X
x = np.arange(len(NAMES_DAYS))
#tamaño de cada barra
width = 0.35

fig, ax = plt.subplots()

#Generamos las barras para el conjunto de hombres
rects1 = ax.bar(x - width/2, trafico_semana_anterior, width, label='Anterior')
#Generamos las barras para el conjunto de mujeres
rects2 = ax.bar(x + width/2, trafico, width, label='Actual')

#Añadimos las etiquetas de identificacion de valores en el grafico
ax.set_ylabel('Trafico')
ax.set_title('Trafico Semanal')
ax.set_xticks(x)
ax.set_xticklabels(NAMES_DAYS)
#Añadimos un legen() esto permite mmostrar con colores a que pertence cada valor.
ax.legend()

autolabel(rects1)
autolabel(rects2)
fig.tight_layout()
plt.savefig('trafico-semanal.png')
#Mostramos la grafica con el metodo show()
#plt.show()

message = (f"El trafico de ayer fue de: {trafico_ayer} visitantes.")

send_email(message)




