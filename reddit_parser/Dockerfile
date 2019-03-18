FROM python:2

WORKDIR /usr/src/app

COPY config.yaml .

COPY parser.py .

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir /var/log/reddit_parser

CMD python parser.py --config_section DEFAULT > /var/log/reddit_parser/parser.log 2>&1