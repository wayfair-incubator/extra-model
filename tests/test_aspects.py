import pandas as pd
import pytest
import spacy
from spacy.symbols import acomp, amod

from extra_model._aspects import (
    adjective_negations,
    adjective_phrase,
    compound_noun_list,
    generate_aspects,
    parse,
)
from extra_model._errors import ExtraModelError


@pytest.fixture()
def spacy_nlp():
    return spacy.load("en_core_web_sm", disable=["ner"])


def test_aspects__compound_noun_list__left_compound(spacy_nlp):
    example_text = "This is a wood screw."
    assert compound_noun_list(spacy_nlp(example_text)[4]) == ["screw", "wood screw"]


@pytest.mark.skip(reason="Left-headed compounds are exceedingly rare in English")
def test_aspects__compound_noun_list__right_compound(spacy_nlp):
    # left-headed compounds are exceedingly rare in english and in 10k
    # example texts, there was not a single one. Could remove the code or could
    # go for a deeper search for an example
    pass


def test_aspects__adjective_phrase_bad_descriptor(spacy_nlp):
    example_text = "this is a text."

    with pytest.raises(ExtraModelError) as exc_info:
        adjective_phrase(spacy_nlp(example_text)[1].head.children, "blurb")

    exception_raised = exc_info.value
    assert (
        str(exception_raised)
        == "descriptor has to be one of [spacy.symbols.acomp, spacy.symbols.amod]"
    )


def test_aspects__adjective_phrase_acomp(spacy_nlp):
    example_text = "The shelf is sturdy and beautiful."
    assert adjective_phrase(spacy_nlp(example_text)[1].head.children, acomp) == [
        "sturdy",
        "beautiful",
    ]


def test_aspects__adjective_phrase_amod(spacy_nlp):
    example_text = "I bought a sturdy and beautiful shelf."
    assert adjective_phrase(spacy_nlp(example_text)[6].children, amod) == [
        "sturdy",
        "beautiful",
    ]


def test_aspects__adjective_phrase_acomp_double_space(spacy_nlp):
    # Spacy parses double space as a token which breaks extra down the line
    example_text = "The shelf is sturdy and  beautiful."
    assert adjective_phrase(spacy_nlp(example_text)[1].head.children, acomp) == [
        "sturdy",
        "beautiful",
    ]


def test_aspects__adjective_phrase_amod_double_space(spacy_nlp):
    # Spacy parses double space as a token which breaks extra down the line
    example_text = "I bought a sturdy and  beautiful shelf."
    assert adjective_phrase(spacy_nlp(example_text)[7].children, amod) == [
        "sturdy",
        "beautiful",
    ]


@pytest.mark.skip(reason="This needs to be looked at when fixing negations")
def test_aspects__adjective_negations__direct(spacy_nlp):
    example_text = "This not so sturdy table is a disappointment."
    assert adjective_negations(spacy_nlp(example_text)[1]) == ["sturdy"]
    # There is a difference here in spacy versions that will need to be investigated.
    # succeeds in 2.0.18 but fails in 3.0.


def test_aspects__adjective_negations__right_non_attr(spacy_nlp):
    example_text = "This color is not pretty."
    assert adjective_negations(spacy_nlp(example_text)[3]) == ["pretty"]


def test_aspects__adjective_negations__right_attr(spacy_nlp):
    example_text = "This is not a terrible table."
    assert adjective_negations(spacy_nlp(example_text)[2]) == ["terrible"]


def test_aspects__parse_multiple_spaces(spacy_nlp, mocker):
    # latest version of spacy parse whitespace as a separate token which sometimes picked up as an adjective
    # we want to make sure that no empty adjectives make it further after parsing
    example_texts = [
        "Wonderful quality - ease in ordering and returning                                     great prices",
        "I bought a sturdy and  beautiful shelf.",
        "Wonderful quality - ease in ordering and returning                             great prices",
    ]
    data_frame = pd.DataFrame(example_texts, columns=["Comments"])
    mocker.patch("spacy.load", return_value=spacy_nlp)
    result = parse(data_frame)
    descriptors = result["descriptor"].tolist()
    assert all([desc.strip() != "" for desc in descriptors])


def test_aspects__parse(spacy_nlp, mocker):
    # chose a text that exercise as much code as possible
    # second part of the sentence is here to check that negations are properly filtered
    example_text = "The wooden cabinet serves its purpose, it's not terrible."
    data_frame = pd.DataFrame([{"Comments": example_text}])
    mocker.patch("spacy.load", return_value=spacy_nlp)
    result = parse(data_frame)
    assert (
        result.iloc[0]["CiD"] == 0
        and result.iloc[0]["position"] == 11
        and result.iloc[0]["aspect"] == "cabinet"
        and result.iloc[0]["descriptor"] == "wooden"
        and not result.iloc[0]["is_negated"]
    )


def test_aspects_generate_aspects(spacy_nlp, mocker):
    example_text = "The wooden cabinet serves its purpose, it's not terrible."
    data_frame = pd.DataFrame([{"Comments": example_text}])
    mocker.patch("spacy.load", return_value=spacy_nlp)
    result = generate_aspects(data_frame)
    assert (
        result.iloc[0]["CiD"] == 0
        and result.iloc[0]["position"] == 11
        and result.iloc[0]["aspect"] == "cabinet"
        and result.iloc[0]["descriptor"] == "wooden"
        and not result.iloc[0]["is_negated"]
    )
