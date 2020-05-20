FROM python:3.6-alpine3.10
LABEL Wladimir Morsakov

COPY requirements.txt /tmp/
RUN pip install --requirement /tmp/requirements.txt

WORKDIR /usr/src/app
CMD ["python", "app.py"]

