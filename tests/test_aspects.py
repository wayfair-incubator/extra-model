import pytest

import spacy
from extra_model._aspects import (
    compound_noun_list,
    acomp_list,
    adjective_list,
    adjective_negations,
)


@pytest.fixture()
def spacy_nlp():
    return spacy.load("en_core_web_sm", disable=["ner"])


def test_aspects__compound_noun_list__left_compound(spacy_nlp):
    example_text = "This is a wood screw."
    assert compound_noun_list(spacy_nlp(example_text)[4]) == ["screw", "wood screw"]


def test_aspects__compound_noun_list__right_compound(spacy_nlp):
    # left-headed compounds are exceedginly rare in english and in 10k
    # example texts, there was not a single one. Could remove the code or could
    # go for a deeper search for an example
    pass


def test_aspects__acomp_list(spacy_nlp):
    example_text = "The shelf is sturdy and beautiful."
    acomp_list(spacy_nlp(example_text)[1].head.children) == ["sturdy", "beautiful"]


def test_aspects__adjective_list(spacy_nlp):
    example_text = "I baught a sturdy and beautiful shelf."
    adjective_list(spacy_nlp(example_text)[6].head.children) == ["sturdy", "beautiful"]


def test_aspects__adjective_negations__direct(spacy_nlp):
    example_text = "This not so sturdy table is a disappointment."
    adjective_negations(spacy_nlp(example_text)[3]) == ["sturdy"]


def test_aspects__adjective_negations__right_non_attr(spacy_nlp):
    example_text = "This color is not pretty."
    adjective_negations(spacy_nlp(example_text)[3]) == ["pretty"]


def test_aspects__adjective_negations__right_attr(spacy_nlp):
    example_text = "This is not a terrible table."
    adjective_negations(spacy_nlp(example_text)[2]) == ["terrible"]
