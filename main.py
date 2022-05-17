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

### Other way to send emails
from email.message import EmailMessage
from email.utils import make_msgid
import mimetypes



HOSTNAME = "data.shoppertrak.com"
USERNAME = "altaplaza"
PASSWORD = "mZZyG9NFWLu*JG"
#PASSWORD = os.environ.get("FTP_CREDENTIALS_SHOPPERTRAK")


NAMES_DAYS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]


class My_Connection(pysftp.Connection):
    def __init__(self, *args, **kwargs):
        self._sftp_live = False
        self._transport = None
        super().__init__(*args, **kwargs)


cnopts = pysftp.CnOpts()
cnopts.hostkeys = None

### Check if file exist and copy if not exist
with My_Connection(
    host=HOSTNAME, username=USERNAME, password=PASSWORD, cnopts=cnopts
) as srv:

    data = srv.listdir()
    for file in data:
        f = Path(f"files/{file}")
        if f.is_file():
            pass
        else:
            srv.get(remotepath=file, localpath=f"./files/{file}")


def read_one_file(day):
    traffic = 0
    with open(f'./files/Extract_{day.strftime("%Y%m%d")}.csv', "r") as datafile:
        csv_file = csv.reader(datafile)
        today = (day - timedelta(days=(1))).strftime("%Y-%m-%d")
        for row in csv_file:
            id, place, door, date, hour, traffic_count, traffic_es, letter = row
            if (today == date and hour != "00:00:00") or (
                day.strftime("%Y-%m-%d") == date and hour == "00:00:00"
            ):
                traffic += int(traffic_count)

    return traffic


def autolabel(rects):
    """Funcion para agregar una etiqueta con el valor en cada barra"""
    for rect in rects:
        height = rect.get_height()
        ax.annotate(
            "{}".format(height),
            xy=(rect.get_x() + rect.get_width() / 2, height),
            xytext=(0, 3),  # 3 points vertical offset
            textcoords="offset points",
            ha="center",
            va="bottom",
        )


def send_email(message, email_to):

    # assign key email aspects to variables for easier future editing
    subject = "Tráfico diario de visitantes"
    body = message
    sender_email = "trafico@altaplazamall.com"
    receiver_email = email_to
    email = MIMEMultipart()
    email["From"] = sender_email
    email["To"] = receiver_email
    email["Subject"] = subject
    email.attach(MIMEText(body, "plain"))
    image = MIMEImage(open("trafico-semanal.png", "rb").read())
    # image.add_header('Content-ID', '<image1>')
    image.add_header(
        "content-disposition", "attachment", filename="%s" % "trafico-semanal.png"
    )
    email.attach(image)
    report = MIMEBase("application", "octate-stream")
    session = smtplib.SMTP("smtp-relay.gmail.com", 587)  # use gmail with port
    session.starttls()  # enable security
    text = email.as_string()
    session.sendmail(sender_email, receiver_email, text)
    session.quit()
    print("Mail Sent")

def send_html_mail(message, email_to):
    msg = EmailMessage()

    # generic email headers
    msg['Subject'] = 'Tráfico diario de visitantes'
    msg['From'] = 'Tráfico Altaplaza Mall<trafico@altaplazamall.com>'
    msg['To'] = f'Tráfico Altaplaza Mall<{email_to}>'

    # set the plain text body
    msg.set_content(message)

    # now create a Content-ID for the image
    image_cid = make_msgid(domain='altaplazamall.com')
    # if `domain` argument isn't provided, it will 
    # use your computer's name

    # set an alternative html body
    msg.add_alternative("""\
    <html>
        <body>
            <p>{message}<br>
            </p>
            <img src="cid:{image_cid}">
        </body>
    </html>
    """.format(message=message,image_cid=image_cid[1:-1]), subtype='html')
    # image_cid looks like <long.random.number@xyz.com>
    # to use it as the img src, we don't need `<` or `>`
    # so we use [1:-1] to strip them off


    # now open the image and attach it to the email
    with open('trafico-semanal.png', 'rb') as img:

        # know the Content-Type of the image
        maintype, subtype = mimetypes.guess_type(img.name)[0].split('/')

        # attach it
        msg.get_payload()[1].add_related(img.read(), 
                                            maintype=maintype, 
                                            subtype=subtype, 
                                            cid=image_cid)


    # the message is ready now
    # you can write it to a file
    # or send it using smtplib
    sender_email = "trafico@altaplazamall.com"
    receiver_email = email_to
    session = smtplib.SMTP("smtp-relay.gmail.com", 587)  # use gmail with port
    session.starttls()  # enable security
    text = msg.as_string()
    session.sendmail(sender_email, receiver_email, text)
    session.quit()
    print("Mail Sent")


# read_one_file(day)

trafico = []
trafico_semana_anterior = []
trafico_anno_anterior = []
week_number = datetime.date(datetime.today()).isocalendar()[1]
print(f'Week: {week_number}')
## retornar dias de la semana
weekday = (datetime.now() - timedelta(days=(1))).weekday()
for i in range(7):
    if i - weekday <= 0:
        day = datetime.now() - timedelta(days=(weekday - i))
        previous_day = datetime.now() - timedelta(days=(weekday - i + 7))
        trafico.append(read_one_file(day))
        trafico_semana_anterior.append(read_one_file(previous_day))
        if i - weekday == 0:
            trafico_ayer = read_one_file(day)
    elif i - weekday > 0:
        previous_day = datetime.now() - timedelta(days=(7 - i + weekday))
        trafico.append(0)
        trafico_semana_anterior.append(read_one_file(previous_day))


print(trafico)
print(trafico_semana_anterior)


###### GENERANDO GRAFICA DE BARRAS DE TRAFICO ACTUAL VS SEMANA ANTERIOR #################
# Obtenemos la posicion de cada etiqueta en el eje de X
x = np.arange(len(NAMES_DAYS))
# tamaño de cada barra
width = 0.35

fig, ax = plt.subplots()

# Generamos las barras para el conjunto de hombres
rects1 = ax.bar(x - width / 2, trafico_semana_anterior, width, label="Semana anterior")
# Generamos las barras para el conjunto de mujeres
rects2 = ax.bar(x + width / 2, trafico, width, label="Semana actual")

# Añadimos las etiquetas de identificacion de valores en el grafico
ax.set_ylabel("Tráfico")
ax.set_title("Tráfico Semanal")
ax.set_xticks(x)
ax.set_xticklabels(NAMES_DAYS)
# Añadimos un legen() esto permite mmostrar con colores a que pertence cada valor.
ax.legend()

autolabel(rects1)
autolabel(rects2)
fig.tight_layout()
plt.savefig("trafico-semanal.png")
# Mostramos la grafica con el metodo show()
# plt.show()

if trafico_ayer != 0:
    message = f"El tráfico de ayer fue de: {trafico_ayer} visitantes."
    #send_html_mail(message, "soporte@altaplazamall.com")
else:
    message = "Tráfico es 0, revisar"
    #send_html_mail(message, "soporte@altaplazamall.com")
