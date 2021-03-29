import os

import pytest
from gensim.models import KeyedVectors

from extra_model._vectorizer import Vectorizer


@pytest.fixture()
def vec():
    # preprocess plain-text test embeddings to proper binary format for vectorizer
    glove_file = "tests/resources/test_adjectives.vec"
    prepro_file = "tests/resources/test_adjectives.prepro"
    model = KeyedVectors.load_word2vec_format(glove_file, binary=False, no_header=True)
    model.save(prepro_file)

    yield Vectorizer(prepro_file)

    # cleanup
    os.remove(prepro_file)


def test__word_exists(vec):
    res = vec.get_vector("little")
    assert res is not None


def test__word_doesnt_exist(vec):
    res = vec.get_vector("gibberrish")
    assert res is None


def test__subword_doesnt_exist(vec):
    res = vec.get_vector("gibberish little")
    assert res is None


def test__compound_word_exists(vec):
    res = vec.get_vector("little small")
    assert res is not None
