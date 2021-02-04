"""do some filtering on the text input:
 -comments need to be not empty
 -a few letters long
 -in egnlish Langage
"""
import logging

import pandas as pd
import pycld2 as cld2

logger = logging.getLogger(__name__)


def filter(dataframe):
    """
    Filter a dataframe for language and text length, also remove unprintable unicode characters
    :param dataframe: (pandas.dataframe): dataframe to be filtered
    :return the filtered dataframe
    """
    # 'None' comments would lead to cashes later
    dataframe = dataframe[pd.notnull(dataframe["Comments"])]
    # reset here to avoid "copy of slice" warning
    dataframe = dataframe.reset_index(drop=True)

    # filter on comment length
    dataframe.loc[:, "cl"] = dataframe.Comments.apply(
        lambda com: len(com) if com is not None else 0
    )
    dataframe = dataframe[dataframe.cl > 20]

    # remove problemaric unicode characters
    dataframe.loc[:, "Comments"] = dataframe.Comments.apply(
        lambda com: "".join(x for x in com if x.isprintable())
    )

    # detect language and filter english. If it's 'unknown' it's probably
    # still english
    dataframe.loc[:, "lang"] = dataframe.Comments.apply(
        lambda com: cld2.detect(com)[2][0][1]
    )
    dataframe = dataframe[(dataframe["lang"] == "en") | (dataframe["lang"] == "un")]

    # drop auxiliary columns again, re-index
    dataframe.drop(["cl", "lang"], axis="columns", inplace=True)
    dataframe.reset_index(inplace=True, drop=True)

    return dataframe
