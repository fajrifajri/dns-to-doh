FROM python:3.6-slim-stretch

COPY . /dnsserver
WORKDIR /dnsserver 

RUN pip3 install --upgrade request\
    && pip3 install dnslib

CMD python3 -u ./dns-to-doh.py