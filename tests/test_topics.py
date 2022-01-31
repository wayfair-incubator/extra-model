import os

import networkx as nx
import numpy as np
import pytest
from gensim.models import KeyedVectors
from nltk.corpus import wordnet as wn

from extra_model._topics import (
    aggregate,
    filter_aggregates,
    get_nodevec,
    has_connection,
    iterate,
    path_to_graph,
    traverse_tree,
)
from extra_model._vectorizer import Vectorizer


@pytest.fixture()
def minivec():
    # preprocess plain-text test embeddings to proper binary format for vectorizer
    glove_file = "tests/resources/test_topics.vec"
    prepro_file = "tests/resources/test_topics.prepro"
    model = KeyedVectors.load_word2vec_format(glove_file, binary=False, no_header=True)
    model.save(prepro_file)

    yield Vectorizer(prepro_file)

    # cleanup
    os.remove(prepro_file)


@pytest.fixture()
def vec():
    return Vectorizer("tests/resources/small_embeddings")


@pytest.fixture()
def simple_graph():
    # a simple example graph: two leaf nodes (corresponding to text instances), L1 and L2, connected to
    # the root of the tree R via two intermidate nodes I1 and I2 which represent higher-level wordnet synsets
    # the edges are weighted to test the similarity functionality
    graph = nx.DiGraph()
    graph.add_nodes_from(["L1", "I1", "L2", "I2", "R"])
    graph.add_edges_from([("L1", "I1"), ("L2", "I2"), ("I1", "R"), ("I2", "R")])
    graph.nodes["L1"]["seed"] = True
    graph.nodes["L2"]["seed"] = True
    graph.nodes["I1"]["seed"] = False
    graph.nodes["I2"]["seed"] = False
    graph.nodes["R"]["seed"] = False
    graph["L1"]["I1"]["similarity"] = 1.0
    graph["L2"]["I2"]["similarity"] = 1.0
    graph["I1"]["R"]["similarity"] = 0.5
    graph["I2"]["R"]["similarity"] = 0.5
    return graph


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
        and graph.nodes[noun]["seed"] is True
    )
    # all the other nodes should not be seeds
    for depth, nodes in nx.dfs_successors(graph, noun).items():
        for node in nodes:
            assert not graph.nodes[node]["seed"]
    # all intermediate nodes should have 2 connections, the leaf only one.
    for depth, nodes in nx.dfs_predecessors(graph, "entity.n.01").items():
        for node in nodes:
            if graph.nodes[node]["seed"] is True:
                assert graph.degree(node) == 1
            else:
                assert graph.degree(node) == 2
    print(graph.nodes)


def test__get_nodevec(minivec):
    assert (get_nodevec("entity.n.01", minivec) == [1.0, 0.0, 0.0, 0.0]).all()


def test__iterate():
    transition_matrix = np.array([[0.0, 1.0], [1.0, 0.0]])
    original = np.array([0.2, 0.8])
    importance = original.copy()
    result = iterate(transition_matrix, importance, original, 0.5)
    assert result[0] == pytest.approx(0.5)
    assert result[1] == pytest.approx(0.5)


def test__has_connection(simple_graph):
    assert (
        has_connection("L1", "R", simple_graph)
        and has_connection("R", "L1", simple_graph)
        and not has_connection("L1", "L2", simple_graph)
    )


def test__filter_aggregates(simple_graph):
    topics = [("L1", 0), ("I1", 0), ("I2", 0), ("L2", 0)]
    filtered, removed = filter_aggregates(topics, simple_graph)
    assert filtered == [("L1", 0), ("I2", 0)] and removed == {
        "I2": ["L2"],
        "L1": ["I1"],
    }


def test__aggregate(vec):
    res, tree = aggregate(
        ["chair", "Chair", "zombie", "unknown"],
        {"chair": 4, "Chair": 2, "zombie": 1, "unknown": 1},
        [
            wn.synset("chair.n.01"),
            wn.synset("chair.n.01"),
            wn.synset("zombi.n.01"),
            None,
        ],
        vec,
    )
    nodes, importances = zip(*res)
    assert (  # first entry should have highest importance because we put high count to it
        importances.index(max(importances)) == 0
    )


def test__traverse_tree__down_weighted(simple_graph):
    assert traverse_tree(
        [("R", 1)],
        {},
        {"L1": 4, "L2": 1},
        simple_graph,
        weighted=True,
        direction="down",
    ) == {"L1": 2, "L2": 0.5}


def test__traverse_tree__down_unweighted(simple_graph):
    assert traverse_tree(
        [("R", 1)],
        {},
        {"L1": 4, "L2": 1},
        simple_graph,
        weighted=False,
        direction="down",
    ) == {"L1": 4, "L2": 1}


def test__traverse_tree__up_weighted(simple_graph):
    assert traverse_tree(
        [("I1", 1)], {}, {"L1": 4, "L2": 1}, simple_graph, weighted=True, direction="up"
    ) == {"L1": 4}


def test__traverse_tree__up_unweighted(simple_graph):
    assert traverse_tree(
        [("I1", 1)],
        {},
        {"L1": 4, "L2": 1},
        simple_graph,
        weighted=False,
        direction="up",
    ) == {"L1": 4}


@pytest.mark.skip(
    reason="This function is hard to test in isolation and is tested as part of the integration test"
)
def test_aspects__get_topics():
    pass


@pytest.mark.skip(
    reason="This function is hard to test in isolation and is tested as part of the integration test"
)
def test_aspects__collect_topic_info():
    pass
