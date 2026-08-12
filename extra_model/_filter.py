import logging

import langdetect
import pandas as pd

# langdetect is non-deterministic unless its seed is fixed, so the same comment can
# be detected as a different language from run to run. Since non-English comments are
# dropped below, that would make the set of surviving comments -- and therefore the
# output -- vary between identical runs.
langdetect.DetectorFactory.seed = 0

logger = logging.getLogger(__name__)


def filter(dataframe):
    """Filter a dataframe for language and text length.

    The following rules apply:
    1. Only comments with at least 20 characters retained.
    2. Only comments in English are retained.
    3. All unprintable unicode characters are removed.

    :param dataframe: dataframe to be filtered. Must have column "Comments"
    :type pd.DataFrame
    :return: Filtered dataframe
    :rtype: pd.DataFrame
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

    # remove problematic unicode characters
    dataframe.loc[:, "Comments"] = dataframe.Comments.apply(
        lambda com: "".join(x for x in com if x.isprintable())
    )

    # detect language and filter english. If it's 'unknown' it's probably
    # still english
    dataframe.loc[:, "lang"] = dataframe.Comments.apply(
        lambda com: langdetect.detect(com)
    )
    dataframe = dataframe[(dataframe["lang"] == "en")]

    # drop auxiliary columns again, re-index
    dataframe = dataframe.drop(["cl", "lang"], axis="columns")
    dataframe = dataframe.reset_index(drop=True)

    return dataframe
