FROM python:3.8-slim-buster

RUN mkdir /package
COPY . /package
WORKDIR /package

RUN pip install --upgrade pip wheel setuptools

RUN pip install --use-deprecated=legacy-resolver -r requirements.txt -r requirements-test.txt
RUN pip install --use-deprecated=legacy-resolver -e .

# download nltk resources
RUN python -m nltk.downloader wordnet
RUN python -m nltk.downloader punkt

# download spacy resources
RUN python -m spacy download en_core_web_sm

CMD bash
