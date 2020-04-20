FROM python:3-alpine
LABEL Wladimir Morsakov

COPY requirements.txt /tmp/
RUN pip install --requirement /tmp/requirements.txt

WORKDIR /usr/src/app
CMD ["python", "app.py"]

