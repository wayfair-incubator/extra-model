import os

import pandas
import pytest
from gensim.models import KeyedVectors

from extra_model._adjectives import (
    adjective_info,
    cluster_adjectives,
    fill_sentiment_dict,
    sentiments_from_adjectives,
)
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


def test__cluster_adjectives__empty(vec):
    # should return False if only unknown adjectives appear
    assert not cluster_adjectives(adjective_counts=[("asdf", 1)], vectorizer=vec)


def test__cluster_adjectives__single(vec):
    # test special case if there is only one adjective
    assert cluster_adjectives(adjective_counts=[("small", 1)], vectorizer=vec) == (
        ["small"],
        [[1]],
        [[("small", 1)]],
    )


def test__cluster_adjectives__common(vec):
    # test the common case with more than one cluster
    # test embeddings for 'ugly' and 'beautiful' are artificially close together to test
    # antonym removal functionality
    adjective_counts = [("small", 23), ("little", 22), ("Beautiful", 19), ("Ugly", 1)]
    assert cluster_adjectives(adjective_counts=adjective_counts, vectorizer=vec) == (
        ("small", "Beautiful", "Ugly"),
        (45, 19, 1),
        ([("small", 23), ("little", 22)], [("Beautiful", 19)], [("Ugly", 1)]),
    )


def test__fill_sentiment_dict():
    assert fill_sentiment_dict([[("Ugly", 1)]]) == {"Ugly": (-0.5106, -1.0)}


def test__sentiments_from_adjectives():
    assert sentiments_from_adjectives(
        [("pretty", 3), ("ugly", 1)], {"pretty": (0.5, 1), "ugly": (-0.5, -1)}
    ) == (0.25, 0.5)


def test__adjective_info(vec):
    # important part here is to test the inversion of the sentiment of negated adjectives
    df_topics = pandas.DataFrame([{"rawterms": ["chair"]}])
    df_aspects = pandas.DataFrame(
        [
            {"aspect": "chair", "descriptor": "beautiful", "is_negated": False},
            # should not drag down score
            {"aspect": "chair", "descriptor": "ugly", "is_negated": True},
            # should  drag down score
            {"aspect": "chair", "descriptor": "ugly", "is_negated": False},
            {"aspect": "chair", "descriptor": "small", "is_negated": False},
            {"aspect": "chair", "descriptor": "little", "is_negated": False},
            # test for unknown adjectives
            {"aspect": "chair", "descriptor": "asdf", "is_negated": False},
        ]
    )
    dft, dfa = adjective_info(df_topics, df_aspects, vec)
    assert (
        # beautiful has potisitve sentiment
        dfa.iloc[0]["sentiment_compound"] > 0
        and dfa.iloc[0]["sentiment_binary"] == 1
        # negated ugly has positive sentiment
        and dfa.iloc[1]["sentiment_compound"] > 0
        and dfa.iloc[1]["sentiment_binary"] == 1
        # straight ugly has negative sentiment
        and dfa.iloc[2]["sentiment_compound"] < 0
        and dfa.iloc[2]["sentiment_binary"] == -1
        # small has neutral sentiment
        and dfa.iloc[3]["sentiment_compound"] == 0
        and dfa.iloc[3]["sentiment_binary"] == 0
        # unkown word has neutral sentiment
        and dfa.iloc[5]["sentiment_compound"] == 0
        and dfa.iloc[5]["sentiment_binary"] == 0
        # do we have correct counts?
        and dft.iloc[0]["adjectives"]
        == [("ugly", 2), ("beautiful", 1), ("small", 1), ("little", 1), ("asdf", 1)]
        and dft.iloc[0]["adjective_clusters"]
        # clustering drops the unkonw word
        == (
            ("ugly", "beautiful", "small"),
            (3, 1, 1),
            ([("ugly", 2), ("little", 1)], [("beautiful", 1)], [("small", 1)]),
        )
        # negated and bare 'ugly' should cancel,
        # TODO: reactivate this test, once adjectives has been reviewed
        # https://projecthub.service.csnzoo.com/browse/AUXEM-42
        # and dft.iloc[0]["sentiment_compound"] == pytest.approx(0)
        # and dft.iloc[0]["sentiment_binary"] == pytest.approx(0)
    )
