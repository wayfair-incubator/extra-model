FROM python:3.6-buster

RUN mkdir /io
COPY . /io
WORKDIR /io

RUN pip install --upgrade pip wheel setuptools

RUN pip install -r requirements.txt -r requirements-test.txt
RUN pip install -e .

# download nltk resources
RUN python -m nltk.downloader wordnet
RUN python -m nltk.downloader punkt

# download spacy resources
RUN python -m spacy download en_core_web_sm
RUN python -m nltk.downloader wordnet

CMD bash
