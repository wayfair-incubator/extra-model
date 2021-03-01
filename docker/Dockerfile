FROM python:3.6-buster

RUN mkdir /package
COPY . /package
WORKDIR /package

RUN pip install --upgrade pip wheel setuptools

RUN pip install -r requirements.txt -r requirements-test.txt
RUN pip install -e .

# download nltk resources
RUN python -m nltk.downloader wordnet
RUN python -m nltk.downloader punkt

# download spacy resources
RUN python -m spacy download en_core_web_sm

CMD bash
