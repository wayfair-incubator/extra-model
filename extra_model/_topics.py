"""Aggregate aspects into semantic clusters ('topics')"""
import logging
from collections import Counter

import networkx as nx
import numpy as np
import pandas as pd
from networkx.algorithms import approximation
from nltk import tokenize
from nltk.corpus import wordnet as wn
from scipy.spatial import distance

from extra_model._disambiguate import match, match_from_single
from extra_model._vectorizer import Vectorizer

logger = logging.getLogger(__name__)


def path_to_graph(hypernym_list, initialnoun):
    """make a hypernym chain into a graph"""
    graph = nx.DiGraph()
    # mark the original word as 'seed' so we can track 'importance' later
    graph.add_node(initialnoun, seed=True)
    previous = initialnoun
    for hypernym in reversed(hypernym_list):
        # we'll take care of the distances later
        graph.add_edge(previous, hypernym.name(), similarity=1.0, distance=1.0)
        graph.nodes[hypernym.name()]["seed"] = False
        previous = hypernym.name()
    return graph


def get_nodevec(node, vectors):
    """get the vector representation of a gloss a wordnet node
    (used to evaluate similarity between rungs in the hypernym chain)"""
    desc = tokenize.word_tokenize(wn.synset(node).definition())
    desc = [vectors.get_vector(word) for word in desc]
    desc = [word for word in desc if word is not None]
    desc = np.sum(desc, axis=0)
    desc = np.divide(desc, np.linalg.norm(desc))
    return desc


def iterate(transition_matrix, importance, original, alpha):
    """find the stable importance vector by iterated multiplication with the distance matrix"""
    importance = np.matmul(transition_matrix, importance)
    importance = np.multiply(importance, alpha)
    importance = np.add(
        importance, np.multiply(np.divide(original, np.sum(original)), 1.0 - alpha)
    )
    importance = np.divide(importance, np.sum(importance))
    return importance


def aggregate(aspects, aspect_counts, synsets_match, vectors):  # noqa: C901
    """aggregate the aspects by building a tree from the hypernym chains
    and using a page-rank type algorithm to assign importance to the nodes in the graph
    we only consider wordnet entries for this, not the actual aspects extracted from the texts"""

    # count how many aspects are matched to a given wornet entry, so that we
    # can remove ambiguities from the graph

    synset_matchnumbers = {}
    for syns in synsets_match:
        if syns in synset_matchnumbers:
            synset_matchnumbers[syns] = synset_matchnumbers[syns] + 1
        else:
            synset_matchnumbers[syns] = 1

    # produce the tree from the hypernym chains
    # a linear graph for every hypernym chain starting from every original
    # aspect
    linear_graphs = []
    for noun, meaning in zip(aspects, synsets_match):
        if meaning is None:  # my life, my code
            continue
        hypernym_paths = meaning.hypernym_paths()
        # if only one hypernym path exists we don't have to select by
        # length/number of connected aspects
        if len(hypernym_paths) == 1:
            linear_graphs.append(path_to_graph(hypernym_paths[0], noun))
            continue
        path_match_nums = [
            np.sum(
                [
                    synset_matchnumbers[syns] if syns in synset_matchnumbers else 0
                    for syns in path
                ]
            )
            for path in hypernym_paths
        ]
        max_match = max(path_match_nums)
        # we need to do the forloop here, because it's possible to have two
        # chains with equal numbers of attached aspects
        for n in range(len(hypernym_paths)):
            if path_match_nums[n] == max_match:
                linear_graphs.append(path_to_graph(hypernym_paths[n], noun))

    # create the full graph as union of all the hypernym chains and lable
    # leaf-nodes
    full_tree = nx.compose_all(linear_graphs)
    # add similarity scores
    for from_node, to_node in full_tree.edges():
        # similarity is only useful within wordnet
        if not full_tree.nodes[from_node]["seed"]:
            full_tree.edges[from_node, to_node]["distance"] = distance.cosine(
                get_nodevec(from_node, vectors), get_nodevec(to_node, vectors)
            )
            full_tree.edges[from_node, to_node]["similarity"] = (
                1.0 - full_tree.edges[from_node, to_node]["distance"]
            )

    # Remove loops with steiner approximation
    seeds = [
        node for node, node_data in full_tree.nodes(data=True) if node_data["seed"]
    ]
    pruned_tree = approximation.steiner_tree(
        full_tree.to_undirected(), seeds, weight="distance"
    )
    pruned_nodes = set(pruned_tree.nodes())
    nodes_to_remove = set(full_tree.nodes())
    nodes_to_remove.difference_update(pruned_nodes)
    full_tree.remove_nodes_from(nodes_to_remove)
    wordnet_nodes = [
        node for node, node_data in full_tree.nodes(data=True) if not node_data["seed"]
    ]

    # produce the similarity matrix
    transition_matrix = np.zeros((len(wordnet_nodes), len(wordnet_nodes)))
    # diagonal needs to be unity
    for n_node in range(len(wordnet_nodes)):
        transition_matrix[n_node][n_node] = 1.0
    wordnet_nodes_indices = dict(
        zip(wordnet_nodes, [i for i in range(len(wordnet_nodes))])
    )
    for from_node, to_node, similarity in full_tree.edges(data="similarity"):
        if not full_tree.nodes[from_node]["seed"]:  # skip the seed nodes for this
            transition_matrix[wordnet_nodes_indices[to_node]][
                wordnet_nodes_indices[from_node]
            ] = similarity

    # start with the an innitial importance weight proportional to the number
    # of mentions of linked aspects in the reviews
    importance_vec = []
    for node in wordnet_nodes:
        imp = 0
        for neighbor in full_tree.predecessors(node):
            if full_tree.node[neighbor]["seed"]:
                imp = imp + aspect_counts[neighbor]
        importance_vec.append(imp)

    importance = np.array(importance_vec)
    importance = np.divide(importance, np.sum(importance))
    importance_original = importance.copy()

    # find the fixed point of the page-rank-algorithm
    for i in range(100):
        importance = iterate(
            transition_matrix, importance, importance_original, 0.5
        )  # XXX make alpha configurable

    # sort the resulting topics by importnace
    topics = list(zip(wordnet_nodes, importance))
    topics = sorted(topics, key=lambda pair: pair[1], reverse=True)
    logger.debug(topics)
    return topics, full_tree  # we still need the tree for filtering


def traverse_tree(  # noqa: C901
    node_list, associated_aspects, aspect_counts, full_tree, weighted, direction
):
    """find all hypernyms/hyponyms in the tree to a given node and aggregate the number of associated mentions
    in the original texts, optionally weighted by term-similarity"""
    new_nodes = []
    for node, weight in node_list:
        for daughter in full_tree.predecessors(node):
            # we need the directed unpruned graph here to avoid descent from
            # hypernyms
            if full_tree.node[daughter]["seed"] and daughter not in associated_aspects:
                associated_aspects[daughter] = aspect_counts[daughter] * weight
        maybe_daugthers = None
        if direction == "up":
            maybe_daugthers = full_tree.neighbors(node)
        if direction == "down":
            maybe_daugthers = full_tree.predecessors(node)
        for daughter in maybe_daugthers:
            if full_tree.node[daughter]["seed"]:  # we already too care of these
                continue
            elif weighted:  # go further up/down the tree
                new_nodes.append(
                    (
                        daughter,
                        weight
                        * (
                            full_tree.edges[node, daughter]["similarity"]
                            if direction == "up"
                            else full_tree.edges[daughter, node]["similarity"]
                        ),
                    )
                )
            else:
                new_nodes.append((daughter, 1))
    if len(new_nodes) == 0:
        return associated_aspects
    else:
        return traverse_tree(
            new_nodes, associated_aspects, aspect_counts, full_tree, weighted, direction
        )


def collect_topic_info(filtered_topics, removed_topics, aspect_counts, full_tree):
    """gather various bits of information into a single DataFrame
    specifically for each topic we store the importance, the list of associated raw text terms and their numbers
    """
    row_vec = []
    for topic in filtered_topics:
        topic_noun = topic[0]
        row = {
            "topic": topic_noun,
            "importance": topic[1],
            "rawterms": [],
            "rawnums": [],
            "weightedterms": [],
            "weights": [],
        }
        logger.debug("Common terms for aspect {0!s} (by raw number)".format(topic_noun))
        raw_aspects = {}
        subsidiaries = removed_topics[topic_noun]
        subsidiaries.append(topic_noun)
        logger.debug(subsidiaries)
        for subtopic in subsidiaries:
            for aspect, count in aspect_counts.items():
                if full_tree.has_edge(aspect, subtopic):
                    raw_aspects[aspect] = count
        if len(raw_aspects) == 0:
            logger.debug("No attached terms, skipping")
            continue
        ordered_aspects = sorted(
            raw_aspects.items(), key=lambda pair: pair[1], reverse=True
        )
        row["rawterms"] = list(list(zip(*ordered_aspects))[0])
        row["rawnums"] = list(list(zip(*ordered_aspects))[1])
        for j in range(min(20, len(ordered_aspects))):  # print some exampels
            logger.debug("{} {}".format(ordered_aspects[j][0], ordered_aspects[j][1]))
        logger.debug(
            "Common terms for aspect {0!s} (distance weighted)".format(topic_noun)
        )
        weighted_aspects = traverse_tree(
            [(topic_noun, 1)],
            {},
            aspect_counts,
            full_tree,
            weighted=True,
            direction="down",
        )
        ordered_aspects_weighted = sorted(
            weighted_aspects.items(), key=lambda pair: pair[1], reverse=True
        )
        row["weightedterms"] = list(list(zip(*ordered_aspects_weighted))[0])
        row["weights"] = list(list(zip(*ordered_aspects_weighted))[1])
        for j in range(min(20, len(ordered_aspects_weighted))):
            logger.debug(
                "{} {}".format(
                    ordered_aspects_weighted[j][0], ordered_aspects_weighted[j][1]
                )
            )
        row_vec.append(row)

    dataframe_topics = pd.DataFrame(
        row_vec,
        columns=[
            "topic",
            "importance",
            "rawterms",
            "rawnums",
            "weightedterms",
            "weights",
        ],
    )
    return dataframe_topics


def has_connection(term, prior, full_tree):
    """check if two terms are connected within the directed hyopernym graph """
    if term in nx.descendants(full_tree, prior) or prior in nx.descendants(
        full_tree, term
    ):
        return True
    return False


def filter_aggregates(topics, tree):
    """filter the importance-sorted list, so that each remaining topic is the sole member of its hypernym chain"""
    filtered_topics = []
    removed_topics = {}
    for term in topics:
        is_new = True
        colliding_prior = None
        for prior in filtered_topics:
            if has_connection(term[0], prior[0], tree):
                is_new = False
                colliding_prior = prior[0]
                break
        if is_new:
            filtered_topics.append(term)
            removed_topics[term[0]] = []
        else:
            removed_topics[colliding_prior].append(term[0])
            logger.debug("Dropping aspect: {0!s}".format(term))
    return filtered_topics, removed_topics


def get_topics(dataframe_aspects, vectors):
    """
    Generate the semanticall clustered topics from the raw aspects
    :param dataframe_aspects: (pandas.dataframe): the collection of nouns to aggregated into topics
    :param vectors: (Vectorizer): provides embeddings for context clustering and wordsense disammbguation
    """

    # for most of the processing we don't really need the specific aspect
    # instances, but just a dict with the aspects and numbers of appearance
    aspect_counts = Counter(dataframe_aspects["aspect"])
    dataframe_aspects.loc[:, "aspect_count"] = dataframe_aspects["aspect"].apply(
        lambda aspect: aspect_counts[aspect]
    )
    logger.debug(aspect_counts.most_common())

    # match the aspects to dictionary terms, filtering aspects that can't be
    # mathched
    aspects, synsets_match = match(aspect_counts, vectors)
    disambiguation_dict = dict(zip(aspects, synsets_match))
    dataframe_aspects.loc[:, "wordnet_node"] = dataframe_aspects["aspect"].apply(
        lambda aspect: disambiguation_dict[aspect].name()
        if (aspect in disambiguation_dict and disambiguation_dict[aspect] is not None)
        else None
    )

    # build the hypernym graph
    topics, full_tree = aggregate(aspects, aspect_counts, synsets_match, vectors)

    # filter the importance ranked topics, so that only one topic within a
    # given hypernym chain remains
    filtered_topics, removed_topics = filter_aggregates(topics, full_tree)

    logger.debug(filtered_topics)

    # gather information into a more structured format
    dataframe_topics = collect_topic_info(
        filtered_topics, removed_topics, aspect_counts, full_tree
    )

    return dataframe_topics


def attach_to_known_topic(
    dataframe_aspects, dataframe_nouns, dataframe_adjectives, dataframe_texts, embedding
):

    in_columns = dataframe_aspects.columns.values

    # First try: we have already seen the aspect in question.
    dataframe_merged = dataframe_aspects.merge(
        dataframe_nouns,
        how="left",
        left_on="aspect",
        right_on="teaAspect",
        validate="m:1",
    )
    dataframe_matched = dataframe_merged[~pd.isnull(dataframe_merged["teaTopicID"])]

    # second try: for words we havent' seen yet, we find the wordnet node and
    # check if we've seen that node
    dataframe_unassigned = dataframe_merged[pd.isnull(dataframe_merged["teaTopicID"])]
    if len(dataframe_unassigned.index) > 0:
        # if all words have already been seen, we don't need the vectorizer and
        # can skip loading this huge file
        vectors = Vectorizer(embedding)

        # remove the first try of a join
        dataframe_unassigned = dataframe_unassigned[in_columns]
        dataframe_unassigned.loc[:, "wordnet_node"] = dataframe_unassigned.apply(
            lambda row: match_from_single(
                row["aspect"], dataframe_texts["Comments"][row["CiD"]], vectors
            ),
            axis=1,
        )
        # if we can't match to the actual aspects, that field should be empty
        reduced_noun_table = dataframe_nouns[
            ["teaWordNet", "teaTopicID", "talAggregateID"]
        ]
        reduced_noun_table = reduced_noun_table.drop_duplicates()
        dataframe_merged = dataframe_unassigned.merge(
            reduced_noun_table,
            how="left",
            left_on="wordnet_node",
            right_on="teaWordNet",
            validate="m:1",
        )
        dataframe_matched.append(
            dataframe_merged[~pd.isnull(dataframe_merged["teaTopicID"])], sort=False
        )

        dataframe_unassigned = dataframe_merged[
            pd.isnull(dataframe_merged["teaTopicID"])
        ]

    logger.debug(
        "assigned {} of {} aspects, {} unassigned".format(
            len(dataframe_matched.index),
            len(dataframe_aspects.index),
            len(dataframe_unassigned.index),
        )
    )
    logger.debug(dataframe_unassigned[["aspect"]].drop_duplicates())

    dataframe_matched = dataframe_matched.merge(
        dataframe_adjectives,
        how="left",
        left_on=["teaTopicID", "descriptor"],
        right_on=["tedTopicID", "tedDescriptor"],
        validate="m:1",
    )
    logger.debug(
        "assigned {} of {} descriptors, {} unassigned".format(
            len(
                dataframe_matched[~pd.isnull(dataframe_matched["tedDescriptor"])].index
            ),
            len(dataframe_matched.index),
            len(dataframe_matched[pd.isnull(dataframe_matched["tedDescriptor"])].index),
        )
    )
    logger.debug(
        dataframe_matched[pd.isnull(dataframe_matched["tedDescriptor"])][
            "descriptor"
        ].drop_duplicates()
    )

    return dataframe_matched
