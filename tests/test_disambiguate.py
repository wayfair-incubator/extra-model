import math
import os
from collections import Counter

import pytest
from gensim.models import KeyedVectors

from extra_model._disambiguate import best_cluster, cluster, match, vectorize_aspects
from extra_model._vectorizer import Vectorizer


@pytest.fixture()
def vec_cluster():
    # preprocess plain-text test embeddings to proper binary format for vectorizer
    glove_file = "tests/resources/test_disambiguate.vec"
    prepro_file = "tests/resources/test_disambiguate.prepro"
    model = KeyedVectors.load_word2vec_format(glove_file, binary=False, no_header=True)
    model.save(prepro_file)

    yield Vectorizer(prepro_file)

    # cleanup
    os.remove(prepro_file)


@pytest.fixture()
def vec():
    return Vectorizer("tests/resources/small_embeddings")


def test__vectorize_aspects(vec_cluster):
    counts = Counter(["chair", "chair", "table", "unkown"])
    nouns, vecs = vectorize_aspects(counts, vec_cluster)
    assert (
        nouns[0] == "chair"  # should be ordered by fequency, so chair first
        and nouns[1] == "table"
        and (vecs[0] == vec_cluster.get_vector("chair")).all()
        and (vecs[1] == vec_cluster.get_vector("table")).all()
        and len(vecs) == 2  # aggregate identical words and drop unknown
        and len(nouns) == 2
    )


def test__best_cluster__too_few_crash():
    # there need to be at least three vectors for the clustering to make sense
    with pytest.raises(IndexError):
        best_cluster([[1.0, 0.0], [0.0, 0.5]])


def test__best_cluster__too_few_default():
    # for a very low number of vectors (<10) should default to int(sqrt(len(vectors)))
    assert best_cluster([[1.0, 0.0], [0.0, 0.5], [-0.5, -0.5]]) == 1


def test__best_cluster():
    # a ~realistic clusterting example
    vectors = []
    for i in range(100):
        vectors.append(
            [math.sin(math.pi * 2 * i / 100), math.cos(math.pi * 2 * i / 100)]
        )
    assert best_cluster(vectors) == 22


def test__cluster(vec_cluster, mocker):
    # we don't care about cluster size optimization for the test, just make sure we get the conexts aggregated right.
    mocker.patch("extra_model._disambiguate.best_cluster", return_value=2)
    aspects = ["table", "chair", "arm", "leg"]
    aspect_vectors = [vec_cluster.get_vector(aspect) for aspect in aspects]

    contexts = cluster(aspects, aspect_vectors, vec_cluster)
    # example is chosen such that table<->chair and arm<->leg should be each others context
    assert (
        (contexts[0] == aspect_vectors[1]).all()
        and (contexts[1] == aspect_vectors[0]).all()
        and (contexts[2] == aspect_vectors[3]).all()
        and (contexts[3] == aspect_vectors[2]).all()
    )


def test__match(vec):
    # mostly an integration test.
    aspects, synsets = match(
        # use distinct numbers of terms here to obtain definite output ordering (most common first)
        Counter(
            [
                "chair",
                "chair",
                "chair",
                "chair",
                "sofa",
                "sofa",
                "sofa",
                "table",
                "table",
                "asdf",
            ]
        ),
        vec,
    )
    assert (
        aspects[0] == "chair"
        and aspects[1] == "sofa"
        and aspects[2] == "table"
        and aspects[3] == "asdf"
        and synsets[0].name() == "chair.n.01"
        and synsets[1].name() == "sofa.n.01"
        and synsets[2].name() == "table.n.03"  # disambiguation failure
        and not synsets[3]  # no synset for the unknown word
    )
