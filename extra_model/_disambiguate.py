"""Functions to do word-sense disambiguation using artifical contexts."""
import logging
import math

import numpy as np
from nltk import tokenize
from nltk.corpus import wordnet as wn
from scipy.spatial import distance
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

logger = logging.getLogger(__name__)


def vectorize_aspects(aspect_counts, vectorizer):
    """Turn the aspect map into a a vector of nouns and their vector representations, which also filters aspects without embedding.

    :param aspect_counts: (dict): the dictionary with aspect counts
    :param vectorizer: (Vectorizer): the provider of word-embeddings
    :return vectors with representable aspects and their vector embeddings
    """
    aspect_vectors = []
    aspect_nouns = []
    for key, _ in aspect_counts.most_common():
        vec = vectorizer.get_vector(key)
        if vec is not None:
            aspect_nouns.append(key)
            aspect_vectors.append(vec)
    return aspect_nouns, aspect_vectors


def best_cluster(aspect_vectors):
    """
    Find the optimal cluster size using silhouette scores.

    :param aspect_vectors:  list of embeddings vectors to be clustered
    :type aspect_vectors: [:class:`numpy.array`]
    :return: the optimal number of clusters
    :rtype: int
    """
    # search a decent number of cluster-numbers for the optimum, but don't get
    # excessive
    min_cluster = 10
    max_cluster = 600
    step_cluster = 20
    safety_margin = 0.6

    silhouette_score_dict = {}
    for cluster_count in range(2, min(max_cluster, len(aspect_vectors)), step_cluster):
        kmeans_clustering = KMeans(n_clusters=cluster_count, random_state=1)
        kmeans_clustering.fit(aspect_vectors)
        silhouette_score_dict[cluster_count] = silhouette_score(
            aspect_vectors, kmeans_clustering.labels_, metric="euclidean"
        )
        logger.debug(
            "{0:d} : {1:f}".format(cluster_count, silhouette_score_dict[cluster_count])
        )
    best = sorted(
        silhouette_score_dict.items(), key=lambda item: item[1], reverse=True
    )[0][0]
    logger.debug("best cluster: {0:d}".format(best))
    logger.debug(
        sorted(silhouette_score_dict.items(), key=lambda item: item[1], reverse=True)
    )
    # return a decent default if clustering doesn't converge
    if best < min_cluster or best > safety_margin * min(
        max_cluster, len(aspect_vectors)
    ):
        return int(math.sqrt(len(aspect_vectors)))
    else:
        return best


def cluster(aspects, aspect_vectors, vectorizer):
    """Cluster aspects based on the distance of their vector representations.

    Once clusters are found, use the other aspects in a given cluster to generate the
    context for a specific aspect noun

    :param aspects: list of words for which clusters are generated
    :type aspects: [str]
    :param aspect_vectors:  list of embeddings corresponding to the the aspects
    :type aspect_vectors: [:class:`numpy.array`]
    :param vectorizer: the provider of word-embeddings for context generation
    :type vectorizer: :class:`extra_model._vectorizer.Vectorizer`
    :return: the synthetic context embedding for each of the input aspects
    :rtype: [:class:`numpy.array`]
    """
    # find the best cluster-size and run k-means clustering, resulting
    # clusters will serve as pseudo-contexts for disambiguation
    best = best_cluster(aspect_vectors)
    kmeans_clustering = KMeans(n_clusters=best, random_state=1)
    kmeans_clustering.fit(aspect_vectors)
    label_map = {}
    # map the cluster results on to the indices of the list of aspects
    for label, aspect in zip(kmeans_clustering.labels_, aspects):
        if label not in label_map:
            label_map[label] = [aspect]
        else:
            label_map[label].append(aspect)
    logger.debug(label_map)

    # generate the context for each aspect, i.e. the average of the embeddings
    # of the word in the cluster, excluding the aspect in question
    contexts = []
    for label, aspect in zip(kmeans_clustering.labels_, aspects):
        contexts.append(
            [vectorizer.get_vector(noun) for noun in label_map[label] if noun != aspect]
        )
    contexts = [np.sum(context, axis=0) for context in contexts]
    contexts = [np.divide(context, np.linalg.norm(context)) for context in contexts]

    return contexts


def match(aspect_counts, vectorizer):  # noqa: C901
    """Match a word to a specific wordnet entry, using the vector similarity of the aspects context and the synonym gloss.

    :param aspect_counts: Counter object of aspect->number of occurrence
    :type aspect_counts: :class:`collections.Counter`
    :param vectorizer:  the provider of word-embeddings for context generation
    :type vectorizer: :class:`extra_model._vectorizer.Vectorizer`
    :return list of aspects that have an embedding and best matching wordnet synonym for each aspect (can be None if no match is found)
    :rtype: ([str],[:class:`nltk.wornet.Synset`])
    """
    # prepare vector representations for clustering
    aspects, aspect_vectors = vectorize_aspects(aspect_counts, vectorizer)
    # find clusters of vectors based on the embedding similarity
    contexts = cluster(aspects, aspect_vectors, vectorizer)

    synsets = []
    for aspect in aspects:
        # find synsets for each aspect
        synset = wn.synsets(aspect.lower(), pos=wn.NOUN)
        if len(synset) == 0:
            # wordnet is missing some compounds, if that happens, we try at to
            # sea if we can have matches for constituents
            for subword in aspect.split():
                synset.extend(wn.synsets(subword.lower(), pos=wn.NOUN))
        if len(synset) == 0:
            logger.debug("No wordnet defintion found for: %s" % aspect)
        synsets.append(synset)

    # get vector embeddings for each word sense by doing a bag-of-word
    # embedding for the dictionary difeinition
    synsets_vec = [
        [synonym.definition() for synonym in synset] for synset in synsets
    ]  # get the definitions as string
    synsets_vec = [
        [tokenize.word_tokenize(synonym_def) for synonym_def in synset]
        for synset in synsets_vec
    ]  # tokenize each sting
    synsets_vec = [
        [
            [vectorizer.get_vector(word) for word in synonym_def_word]
            for synonym_def_word in synset
        ]
        for synset in synsets_vec
    ]  # gert the rmbeddding for each token
    synsets_vec = [
        [
            [embedding for embedding in synonym_def_emebd if embedding is not None]
            for synonym_def_emebd in synset
        ]
        for synset in synsets_vec
    ]  # ignore words without embedding
    synsets_vec = [
        [np.sum(synonym_embeddings, axis=0) for synonym_embeddings in synset]
        for synset in synsets_vec
    ]  # sum the embeddings to get a bag-of-words embedding
    synsets_vec = [
        [
            np.divide(synset_embedding, np.linalg.norm(synset_embedding))
            for synset_embedding in synset
        ]
        for synset in synsets_vec
    ]  # normalize

    synsets_match = []
    for noun, context, synset, synset_vec in zip(
        aspects, contexts, synsets, synsets_vec
    ):
        # filter words not represented in wordnet
        if len(synset_vec) == 0:
            synsets_match.append(None)
            continue
        # If only one word-sense is matched we don't have to disambiguate, just
        # take it
        if len(synset_vec) == 1:
            synsets_match.append(synset[0])
            continue
        # If the context-clustering has not yielded a context, we can't
        # really disambuguate, just take the first (i.e. most common) synonym
        if not isinstance(context, np.ndarray) and np.isnan(context):
            synsets_match.append(synset[0])
            continue

        # if there's ambiguity, choose the worde sense with the smallest
        # embedding distance between dictionary definition and noun context
        distances = [distance.cosine(context, synonym) for synonym in synset_vec]
        min_dist, min_index = min((val, idx) for (idx, val) in enumerate(distances))
        synsets_match.append(synset[min_index])
        logger.debug(
            "{0!s} {1!s}  at distance: {2:f}".format(noun, synset[min_index], min_dist)
        )
        logger.debug(synset[min_index].definition())

    return aspects, synsets_match
