import networkx as nx
import numpy as np
import pytest
from gensim.models import KeyedVectors
from gensim.scripts.glove2word2vec import glove2word2vec
from nltk.corpus import wordnet as wn

from extra_model._topics import get_nodevec, path_to_graph, iterate
from extra_model._vectorizer import Vectorizer


@pytest.fixture()
def vec():
    # preprocess plain-text test embeddings to proper binary format for vectorizer
    glove_file = "tests/resources/test_topics.vec"
    tmp_file = "tests/resources/test_topics.tmp"
    _ = glove2word2vec(glove_file, tmp_file)
    model = KeyedVectors.load_word2vec_format(tmp_file)
    model.save("tests/resources/test_topics.prepro")

    return Vectorizer("tests/resources/test_topics.prepro")


def test__path_to_graph():
    noun = "zombie"
    hypernym_list = wn.synsets(noun, pos=wn.NOUN)[0].hypernym_paths()[0]
    graph = path_to_graph(hypernym_list, noun)
    print(list(graph.successors(noun)))
    print(list(graph.successors("entity.n.01")))
    assert (
        # entity is the root
        len(list(graph.successors("entity.n.01"))) == 0
        # initial word is the leaf
        and len(nx.dfs_successors(graph, noun)) == graph.order() - 1
        # leaf has the seed-flag set
        and (graph.nodes[noun]["seed"] == True)
    )
    # all the other nodes should not be seeds
    for depth, nodes in nx.dfs_successors(graph, noun).items():
        for node in nodes:
            assert graph.nodes[node]["seed"] == False
    # all intermediate nodes should have 2 connections, the leaf only one.
    for depth, nodes in nx.dfs_predecessors(graph, "entity.n.01").items():
        for node in nodes:
            if graph.nodes[node]["seed"] == True:
                assert graph.degree(node) == 1
            else:
                assert graph.degree(node) == 2
    print(graph.nodes)


def test__get_nodevec(vec):
    assert (get_nodevec("entity.n.01", vec) == [1.0, 0.0, 0.0, 0.0]).all()


def test__iterate():
    transition_matrix = np.array([[0.0, 1.0], [1.0, 0.0]])
    original = np.array([0.2, 0.8])
    importance = original.copy()
    result = iterate(transition_matrix, importance, original, 0.5)
    assert result[0] == pytest.approx(0.5)
    assert result[1] == pytest.approx(0.5)
