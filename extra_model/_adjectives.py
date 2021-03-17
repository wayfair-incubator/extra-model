"""Cluster adjectives and extract sentiment."""

from collections import Counter

import numpy as np
from nltk.corpus import wordnet as wn
from sklearn.neighbors import BallTree
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


def cluster_adjectives(adjective_counts, vectorizer):  # noqa: C901
    """Cluster adjectives based on a constant radius clustering algorithm.

    Technical implementation uses a scikitlearn BallTree.

    :param adjective_counts: dictionary with adjectives and their counts
    :type adjective_counts: [(str,int)]
    :param vectorizer:  provide embeddings to evaluate adjective similarity
    :type vectorizer: :class:`_vectorizer.vectorizer`
    :return: first list contains the representative words for the adjective clusters,
        second list the size (total number of clustered adjectives) for each cluster,
        third list has for each cluster a list of the constituent adjectives with number of occurence
    :rtype: ([string],[int],[[(string,int)]])
    """
    adjectives, counts = zip(*adjective_counts)
    adjectives = list(adjectives)
    counts = list(counts)

    # find vector embeddings for the adjectives and filter adjectives for which ew don't have an embedding
    # most of these are typos
    vectors = [vectorizer.get_vector(ad) for ad in adjectives]
    for i in range(len(adjectives)):
        if vectors[i] is None:
            adjectives[i] = None
            counts[i] = None
    adjectives = [ad for ad in adjectives if ad is not None]
    counts = [count for count in counts if count is not None]
    vectors = [vec for vec in vectors if vec is not None]
    # keep track of indices for further processing
    indices = [i for i in range(len(adjectives))]
    clusters = []
    cluster_size = []
    # use the adjective closest to the cluster center as representative
    cluster_representative = []
    cluster_ads = []

    if (
        len(vectors) == 0
    ):  # no embeddable adjective for this topic -> there is no cluster to build
        return
    if len(vectors) == 1:  # Balltree doesn't work if list contains a single vector
        # in this case, the single word is the whole cluster
        return (adjectives, [counts], [[(adjectives[0], counts[0])]])
    tree = BallTree(vectors)
    working_set = list(zip(adjectives, indices))
    already_clustered = set()
    # run the constant radius clustering:
    # as long as there are unclustered adjectives left, take the one with the highes count
    # and cluster all other words within a given distance into it.
    while len(working_set) > 0:
        # radius of 0.8 hand-tuned to give decent adjective clusters
        cluster_indices = tree.query_radius([vectors[working_set[0][1]]], 0.8)
        new_cluster = []
        for i in cluster_indices[0]:
            new_cluster.append(i)
        new_cluster = [index for index in new_cluster if index not in already_clustered]
        # clean the new cluster from opposites:
        # get the synset for the most common word in the cluster
        master_synset = wn.synsets(working_set[0][0].lower(), pos=wn.ADJ)
        master_antonyms = set()
        for syn in master_synset:
            for lemma in syn.lemmas():
                master_antonyms.update(lemma.antonyms())
        for i in range(len(new_cluster)):
            # skip the most common word, in case it is among its own antonyms
            # (shouldn't happen)
            if new_cluster[i] == working_set[0][1]:
                continue
            for syn in wn.synsets(adjectives[new_cluster[i]].lower(), pos=wn.ADJ):
                for lemma in syn.lemmas():
                    if lemma in master_antonyms:
                        new_cluster[i] = None
                        break
                if new_cluster[i] is None:
                    break
        new_cluster = [ind for ind in new_cluster if ind is not None]
        already_clustered.update(new_cluster)
        for i in range(len(working_set)):
            if working_set[i][1] in already_clustered:
                working_set[i] = None
        working_set = [it for it in working_set if it is not None]
        clusters.append(new_cluster)
        cluster_size.append(sum(counts[i] for i in new_cluster))
        cluster_ads.append([(adjectives[i], counts[i]) for i in new_cluster])

        # get the representative as closest word to the cluster-mean
        cluster_weights = [counts[i] for i in new_cluster]
        cluster_vecs = [vectors[i] for i in new_cluster]
        cluster_representative.append(
            adjectives[
                tree.query(
                    [np.average(cluster_vecs, axis=(0), weights=cluster_weights)],
                    return_distance=False,
                )[0][0]
            ]
        )

    # sort clusters by size before returning
    cluster_size, cluster_ads, cluster_representative = zip(
        *sorted(
            zip(cluster_size, cluster_ads, cluster_representative),
            key=lambda cluster: cluster[0],
            reverse=True,
        )
    )
    return (cluster_representative, cluster_size, cluster_ads)


def fill_sentiment_dict(adjective_counts):
    """Given a dictionary with adjectives and their counts, will compute.

    The sentiment of each of the adjectives using the VADER sentiment analysis package
    and return a dictionary of the adjectives and their sentiments.

    :param adjective_counts: dictionary with adjectives and their counts
    :type adjective_counts: dict
    :return: dictionary, where the keys are the adjectives and the values are tuples of the
        corresponding compound sentiument and binary sentiment
    :rtype: dict
    """
    sentiment_dict = {}
    analyzer = SentimentIntensityAnalyzer()
    for one_topic_adjectives in adjective_counts:
        for adjective, _ in one_topic_adjectives:
            if adjective not in sentiment_dict:
                score = analyzer.polarity_scores(adjective)
                sentiment_dict[adjective] = (
                    score["compound"],
                    (score["pos"] - score["neg"]),
                )
    return sentiment_dict


def sentiments_from_adjectives(adjective_counts, sentiment_dict):
    """Build the weighted average sentiment score from a list of adjetives and their counts.

    :param adjective_counts: list of tuples with adjectives and their counts
    :type adjective_counts: [(str,int)]
    :param sentiment_dict: dictionary with adjectives and their sentiment, as tuple of compound and binary sentiment
    :type sentiment_dict: dict
    :return: a tuple of the weighted averages of compound and binary sentiment
    :rtype: (float,float)
    """
    cumulative_sentimenent_compound = 0
    cumulative_sentimenent_binary = 0
    for adjective, count in adjective_counts:
        cumulative_sentimenent_compound = (
            cumulative_sentimenent_compound + sentiment_dict[adjective][0] * count
        )
        cumulative_sentimenent_binary = (
            cumulative_sentimenent_binary + sentiment_dict[adjective][1] * count
        )

    total = sum(list(zip(*adjective_counts))[1])
    sentimentscore_compound = cumulative_sentimenent_compound / total
    sentimentscore_binary = cumulative_sentimenent_binary / total

    return (sentimentscore_compound, sentimentscore_binary)


def adjective_info(dataframe_topics, dataframe_aspects, vectorizer):
    """Add adjective related information to the dataframes.

    This has two facets:
    -> for each topic cluster similar adjectives, to get a more abstract/readable list
    -> for each topic, use the adjectives to come up with a sentiment classification

    :param dataframe_topics: the dataframe with the topics we want to enrich, needs to have a collum `rawterms`
    :type dataframe_topics: :class:`pandas.DataFrame`
    :param dataframe_aspects: the dataframe with the aspect instances and related adjectives with columsn `aspect` and `descriptor`
    :type dataframe_aspects: :class:`pandas.DataFrame`
    :param vectorizer:  provide embeddings for the adjectives
    :type vectorizer: :class:`_vectorizer.vectorizer`
    :return: the enriched datafromes
    :rtype: (:class:`pandas.DataFrame`,:class:`pandas.DataFrame`)
    """
    # get counts of adjectives connected to a given topic
    dataframe_topics["adjectives"] = dataframe_topics["rawterms"].apply(
        lambda terms: Counter(
            dataframe_aspects[dataframe_aspects["aspect"].isin(terms)]["descriptor"]
        ).most_common()
    )
    dataframe_topics["adjective_clusters"] = dataframe_topics["adjectives"].apply(
        lambda adjective_counts: cluster_adjectives(adjective_counts, vectorizer)
    )

    # sentimentscore for adjectives, based on compund score of Vader sentiment
    # compound refers to mixed score whereas bin refers to binary weight (1/0) of sentiment
    # use one dict, so we don't need to run the classifier more than once for
    # a single adjective
    sentiment_dict = fill_sentiment_dict(dataframe_topics["adjectives"])
    dataframe_topics["sentiment_pair"] = dataframe_topics["adjectives"].apply(
        lambda adjective_counts: sentiments_from_adjectives(
            adjective_counts, sentiment_dict
        )
    )
    dataframe_topics["sentiment_compound"] = dataframe_topics["sentiment_pair"].apply(
        lambda pair: pair[0]
    )
    dataframe_topics["sentiment_binary"] = dataframe_topics["sentiment_pair"].apply(
        lambda pair: pair[1]
    )

    dataframe_aspects["sentiment_compound"] = dataframe_aspects["descriptor"].apply(
        lambda descriptor: sentiment_dict[descriptor][0]
        if descriptor in sentiment_dict
        else 0
    )
    dataframe_aspects["sentiment_binary"] = dataframe_aspects["descriptor"].apply(
        lambda descriptor: sentiment_dict[descriptor][1]
        if descriptor in sentiment_dict
        else 0
    )

    # flip sentiment if adjective is negated
    dataframe_aspects["sentiment_compound"] = dataframe_aspects.apply(
        lambda x: x["sentiment_compound"] * (-1)
        if x["is_negated"]
        else x["sentiment_compound"],
        axis=1,
    )
    dataframe_aspects["sentiment_binary"] = dataframe_aspects.apply(
        lambda x: x["sentiment_binary"] * (-1)
        if x["is_negated"]
        else x["sentiment_binary"],
        axis=1,
    )
    return dataframe_topics, dataframe_aspects
