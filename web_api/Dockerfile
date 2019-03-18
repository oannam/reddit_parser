FROM python:2.7

ADD . /usr/src/app

WORKDIR /usr/src/app

EXPOSE 8080

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN mkdir /var/log/web_api

CMD python bootstrap.py --config_section DEFAULT > /var/log/web_api/bootstrap.log 2>&1