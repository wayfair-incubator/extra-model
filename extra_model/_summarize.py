"""Fill out and link the dataframes for topics, aspects and texts. Provide some summary ouput if debug-level is set to info or lower."""
import logging

logger = logging.getLogger(__name__)


def qa(dataframe_texts, dataframe_aspects, dataframe_topics):
    """Print summary information.

    :param dataframe_texts: dataframe with the raw texts (for example output)
    :type dataframe_texts: :class:`pandas.DataFrame`
    :param dataframe_aspects:  dataframe with the aspects
    :type dataframe_texts: :class:`pandas.DataFrame`
    :param dataframe_topics: dataframe with the topics
    :type dataframe_texts: :class:`pandas.DataFrame`
    """
    for ind in dataframe_topics.index:
        logger.debug("\n++++++++++++++++++++++++++++++\n")
        logger.debug(
            "analyzing topic {0!s} of importance {1:f}".format(
                dataframe_topics["topic"][ind], dataframe_topics["importance"][ind]
            )
        )
        logger.debug(
            "with seniment {0:f}(compound) / {1:f}(binary)\n".format(
                dataframe_topics["sentiment_compound"][ind],
                dataframe_topics["sentiment_binary"][ind],
            )
        )
        # attached terms by raw number
        logger.debug("Common terms (by raw number)")
        for term, num in zip(
            dataframe_topics["rawterms"][ind], dataframe_topics["rawnums"][ind]
        ):
            logger.debug("{0!s} ({1:d}) ".format(term, num))

        # count attached terms by distance weighted number XXX this section will
        # go after debugginf
        logger.debug("Common terms for aspect (distance weighted)")
        for term, num in zip(
            dataframe_topics["weightedterms"][ind], dataframe_topics["weights"][ind]
        ):
            logger.debug("{0!s} ({1:f}) ".format(term, num))

        # adjective clusters
        if dataframe_topics["adjective_clusters"][ind] is not None:
            logger.debug("\nFound adjective clusters:\n")
            representatives, sizes, adjectives = dataframe_topics["adjective_clusters"][
                ind
            ]
            for representative, size, subads in zip(representatives, sizes, adjectives):
                logger.debug(
                    "For representative: {}({}): ".format(representative, size)
                )
                adstring = ""
                for ad, count in subads:
                    adstring += "{}({}), ".format(ad, count)
                logger.debug(adstring)

            # representative comments (most common term  and most commen
            # adjective)
            logger.debug(
                "\nrepresentative comments (most common term with most common adjective cluster)"
            )
            comments = dataframe_aspects[
                dataframe_aspects["aspect"].isin([dataframe_topics["rawterms"][ind][0]])
                & dataframe_aspects["adcluster"].isin(
                    [dataframe_topics["adjective_clusters"][ind][0][0]]
                )
            ]
            comments = comments.head(5)
            for oi in comments["CiD"]:
                logger.debug(dataframe_texts["Comments"][oi])


def set_aspect(topic, dataframe_aspects):
    """For a given topic, set topic and adjective cluster fields in the aspect_dataframe.

    :param topic: the topic and it's associated information that we need to copy to the relevant entries in the aspect frame
    :type topic: :class:`pandas.DataFrame.Row`
    :param dataframe_aspects: the dataframe to be enriched with topic information
    :type dataframe_aspects: :class:`pandas.DataFrame`
    """
    dataframe_aspects.loc[
        dataframe_aspects["aspect"].isin(topic["rawterms"]), "topicID"
    ] = topic["topicID"]

    # this can happen if there is only a single adjective
    if topic["adjective_clusters"] is not None:
        for representative, all_adjectives in zip(
            topic["adjective_clusters"][0], topic["adjective_clusters"][2]
        ):
            dataframe_aspects.loc[
                dataframe_aspects["aspect"].isin(topic["rawterms"])
                & dataframe_aspects["descriptor"].isin(list(zip(*all_adjectives))[0]),
                "adcluster",
            ] = representative


def link_aspects_to_topics(dataframe_aspects, dataframe_topics):
    """Fill topic and adjective cluster information into the aspect dataframe.

    :param dataframe_aspects: the dataframe to be enriched
    :type dataframe_aspects: :class:`pandas.DataFrame`
    :param dataframe_topics:  the dataframe that has the topic and adjective cluster information
    :type dataframe_topics: :class:`pandas.DataFrame`
    :return: the enriched dataframe
    :rtype: :class:`pandas.DataFrame`
    """
    # create empty collumns to be filled
    dataframe_aspects["topicID"] = None
    dataframe_aspects["adcluster"] = None

    # create a topic-id from the dataframe index
    dataframe_topics.reset_index(inplace=True)
    dataframe_topics.rename({"index": "topicID"}, axis="columns", inplace=True)

    dataframe_topics.apply(lambda topic: set_aspect(topic, dataframe_aspects), axis=1)

    return dataframe_aspects


def link_aspects_to_texts(dataframe_aspects, dataframe_texts):
    """Transfer the original text identifier from the original text data table into the final aspect table.

    :param dataframe_aspects: table to be enriched
    :type dataframe_aspects: :class:`pandas.DataFrame`
    :param dataframe_texts: original table from which this information is extracted
    :type dataframe_texts: :class:`pandas.DataFrame`
    :return: The aspect dataframe which has been enriched with source-information
    :rtype: :class:`pandas.DataFrame`
    """
    # we don't need everything from the original, let's keep only the useful
    # info to safe space on the output table
    keepers = dataframe_aspects.columns.values.tolist()
    keepers.append("source_guid")  # unique identifier for the utterance
    logger.debug("keeping aspects columns: {}".format(keepers))

    # join aspects to the original texts
    dataframe_aspects = dataframe_aspects.join(dataframe_texts, on="CiD")

    return dataframe_aspects[keepers]
