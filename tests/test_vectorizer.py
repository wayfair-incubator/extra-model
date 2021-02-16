import os

import pytest
from gensim.models import KeyedVectors
from gensim.scripts.glove2word2vec import glove2word2vec

from extra_model._vectorizer import Vectorizer


@pytest.fixture()
def vec():
    # preprocess plain-text test embeddings to proper binary format for vectorizer
    glove_file = "tests/resources/test_adjectives.vec"
    tmp_file = "tests/resources/test_adjectives.tmp"
    prepro_file = "tests/resources/test_adjectives.prepro"
    _ = glove2word2vec(glove_file, tmp_file)
    model = KeyedVectors.load_word2vec_format(tmp_file)
    model.save(prepro_file)

    yield Vectorizer(prepro_file)

    # cleanup
    os.remove(tmp_file)
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
