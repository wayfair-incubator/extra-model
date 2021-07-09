import numpy as np
import pandas as pd

from extra_model._summarize import (
    link_aspects_to_texts,
    link_aspects_to_topics,
    qa,
    set_aspect,
)


def test_summarize__qa():
    # Test is a bit tricky, ideally you'd like to run the complete code to see that the output format
    # matches what is expected by this function. However, that's not really feasible for testing,
    # so we mock the respective dataframes just to see that it's not crashing
    topicframe = pd.DataFrame(
        columns=[
            "topic",
            "rawterms",
            "rawnums",
            "weightedterms",
            "weights",
            "topicID",
            "adjective_clusters",
            "importance",
            "sentiment_compound",
            "sentiment_binary",
        ]
    )
    topicframe.loc[0] = np.asarray(
        [
            "table",
            ["table"],
            [1],
            ["table"],
            [1],
            1,
            (["small"], [[1]], [[("small", 1)]]),
            1.0,
            1.0,
            1.0,
        ],
        dtype=object,
    )
    aspectframe = pd.DataFrame(
        [{"aspect": "table", "descriptor": "small", "adcluster": "small", "CiD": 0}]
    )
    textframe = pd.DataFrame([{"Comments": "This is a small table"}])
    # this just needs to not crash
    qa(textframe, aspectframe, topicframe)


def test_summarize__set_aspect():
    topicframe = pd.DataFrame(columns=["rawterms", "topicID", "adjective_clusters"])
    topicframe.loc[0] = np.asarray(
        [["table"], 1, (["small"], [[1]], [[("small", 1)]])], dtype=object
    )
    aspectframe = pd.DataFrame(
        [
            {"aspect": "table", "descriptor": "small"},
            {"aspect": "chair", "descriptor": "small"},
        ]
    )
    aspectframe["topicID"] = None
    aspectframe["adcluster"] = None

    topicframe.apply(lambda topic: set_aspect(topic, aspectframe), axis=1)

    assert (
        aspectframe.iloc[0]["topicID"] == 1
        and aspectframe.iloc[0]["adcluster"] == "small"
        and not aspectframe.iloc[1]["topicID"]
        and not aspectframe.iloc[1]["adcluster"]
    )


def test_summarize__link_aspects_to_topics():
    topicframe = pd.DataFrame(columns=["rawterms", "adjective_clusters"])
    topicframe.loc[0] = np.asarray(
        [["table"], (["small"], [[1]], [[("small", 1)]])], dtype=object
    )
    aspectframe = pd.DataFrame(
        [
            {"aspect": "table", "descriptor": "small"},
            {"aspect": "chair", "descriptor": "small"},
        ]
    )
    result = link_aspects_to_topics(aspectframe, topicframe)
    assert (
        result.iloc[0]["topicID"] == 0
        and aspectframe.iloc[0]["adcluster"] == "small"
        and not aspectframe.iloc[1]["topicID"]
        and not aspectframe.iloc[1]["adcluster"]
        and topicframe.iloc[0]["topicID"] == 0  # has the topicID been added?
    )


def test_summarize__link_aspects_to_texts():
    aspectframe = pd.DataFrame([{"CiD": 0}, {"CiD": 2}])
    textframe = pd.DataFrame(
        [{"source_guid": 1, "drop": 0}, {"source_guid": 2, "drop": 0}]
    )
    result = link_aspects_to_texts(aspectframe, textframe)
    print(result)
    assert (
        result.iloc[0]["source_guid"] == 1  # join the correct text
        and "CiD" in result.columns.values.tolist()  # keep the right cols
        and "source_guid" in result.columns.values.tolist()  # keep the right cols
        and "drop" not in result.columns.values.tolist()  # drop other columns
    )
