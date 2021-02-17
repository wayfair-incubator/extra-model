import pandas as pd
import pytest

from extra_model._filter import filter


@pytest.fixture()
def dataset():
    input_df = pd.DataFrame(
        [
            {"Comments": "This is an example of English comment", "id": "good"},
            {
                "Comments": "Dies ist ein Beispiel für einen deutschen Kommentar",
                "id": "german",
            },
            {"Comments": "Short", "id": "short"},
            {
                "Comments": "This is a comment with \n non-printable sequence",
                "id": "nonprintable",
            },
        ]
    )

    return input_df


@pytest.fixture()
def cleaned_dataset(dataset):
    cleaned = filter(dataset)
    return cleaned


def test__dropping_short_comment(cleaned_dataset):
    ids = cleaned_dataset["id"].tolist()
    assert "short" not in ids


def test__dropping_non_english_comment(cleaned_dataset):
    ids = cleaned_dataset["id"].tolist()
    assert "german" not in ids


def test__no_unreadable_characters(cleaned_dataset):
    nonprintable_id = cleaned_dataset["id"].tolist().index("nonprintable")
    comment = cleaned_dataset["Comments"][nonprintable_id]
    assert comment.isprintable()


def test__proper_comment_is_retained(cleaned_dataset):
    ids = cleaned_dataset["id"].tolist()
    assert "good" in ids
