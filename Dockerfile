FROM python:3.10-slim-buster

COPY requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt

RUN mkdir -p /code
RUN mkdir -p /data/
COPY cosmic_python/*.py /code/
COPY data/* /code/data/

WORKDIR /code/
ENV FLASK_APP=cosmic_python/flask_app.py FLASK_DEBUG=1 PYTHONUNBUFFERED=1
CMD flask run --host=0.0.0.0 --port=80