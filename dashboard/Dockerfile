FROM ubuntu:19.04
LABEL Wladimir Morsakov

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y python3-pip python3 
RUN pip3 install pandas

COPY requirements.txt /tmp/
RUN pip3 install --requirement /tmp/requirements.txt

WORKDIR /usr/src/app
CMD ["python3", "dash_main.py"]

