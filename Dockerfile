FROM python:3

ADD main.py /
ADD requeriments.txt /
RUN pip install -r requeriments.txt
RUN mkdir /files
COPY ./files/* /files/
CMD [ "python", "./main.py" ]