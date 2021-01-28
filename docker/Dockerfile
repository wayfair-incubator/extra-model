FROM python:3.6-buster

RUN mkdir /io
COPY . /io
WORKDIR /io

RUN pip install -r requirements.txt -r requirements-test.txt

CMD bash
