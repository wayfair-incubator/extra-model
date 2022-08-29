FROM python:3.10-slim-buster as builder

COPY requirements.txt requirements-test.txt ./

RUN pip install --prefix=/requirements \
    -r requirements.txt \
    -r requirements-test.txt

ARG PYTHONPATH=/requirements/lib/python3.9/site-packages

# download spacy resources
RUN python -m spacy download en_core_web_sm --prefix=/requirements

# download nltk resources
RUN python -m nltk.downloader wordnet punkt omw-1.4

FROM python:3.10-slim-buster

RUN apt-get update && apt-get install --no-install-recommends --yes \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /root/nltk_data /root/nltk_data
COPY --from=builder /requirements /usr/local

WORKDIR /package
COPY . /package

RUN pip install -e .

CMD bash
