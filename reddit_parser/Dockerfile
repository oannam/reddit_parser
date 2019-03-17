FROM python:2

WORKDIR /usr/src/app

COPY config.yaml .

COPY parser.py .

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

CMD python parser.py --config_section DEFAULT