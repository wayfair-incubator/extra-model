import pytest

import spacy
from extra_model._aspects import compound_noun_list, acomp_list, adjective_list


@pytest.fixture()
def spacy_nlp():
    return spacy.load("en_core_web_sm", disable=["ner"])


def test_aspects__compound_noun_list__left_compound(spacy_nlp):
    example_text = "This is a wood screw."
    assert compound_noun_list(spacy_nlp(example_text)[4]) == ["screw", "wood screw"]


def test_aspects__compound_noun_list__right_compound(spacy_nlp):
    # XXX find example
    example_text = "This is a wood screw."
    assert compound_noun_list(spacy_nlp(example_text)[4]) == ["screw", "wood screw"]


def test_aspects__acomp_list(spacy_nlp):
    example_text = "The shelf is sturdy and beautiful."
    acomp_list(spacy_nlp(example_text)[1].head.children) == ["sturdy", "beautiful"]


def test_aspects__adjective_list(spacy_nlp):
    example_text = "I baught a sturdy and beautiful shelf."
    adjective_list(spacy_nlp(example_text)[6].head.children) == ["sturdy", "beautiful"]


def test_aspects__adjective_negations(spacy_nlp):
    pass
