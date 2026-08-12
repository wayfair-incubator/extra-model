FROM python:3.13-slim-bookworm as builder

COPY requirements.txt requirements-test.txt ./

# the en_core_web_sm pipeline is pinned in requirements.txt, so no
# `python -m spacy download` step is needed here
RUN pip install --prefix=/requirements \
    -r requirements.txt \
    -r requirements-test.txt

ARG PYTHONPATH=/requirements/lib/python3.13/site-packages

# download nltk resources. punkt_tab (not punkt) is what word_tokenize
# needs from nltk 3.8.2 onwards
RUN python -m nltk.downloader wordnet punkt_tab omw-1.4

FROM python:3.13-slim-bookworm

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
