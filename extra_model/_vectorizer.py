import logging

import numpy as np
from gensim.models import KeyedVectors

logger = logging.getLogger(__name__)


class Vectorizer:
    """Simple Vectorizer class using pre-trained vectors."""

    def __init__(self, embedding_file):
        """
        Use the generic gensim vector embedding lookup.

        Currently using pretrained glove embeddings, but anything goes.
        :param embedding_file: pathname for the file that stores the word-embeddings in gensim keyed-vectors format
        :type str
        """
        self.wv_glove = KeyedVectors.load(embedding_file, mmap="r")

    def get_vector(self, key):
        """
        Return the vector embedding for a given word.

        According to the following logic:
            - if no embedding is found for this word, check if it's a compound
            - if it's a compound try to take the average embedding of the constituent words
            - if a that fails too, return None, downstream code will have to deal with the absence of an embedding
        (typical course of action is to ignore such a term)
        :param key: the word to be embedded
        :type str
        :return: the embedding vector. Number of dimensions is set by the input file
        :rtype np.array:
        """
        if key.lower() in self.wv_glove.key_to_index:
            return self.wv_glove.get_vector(key.lower(), norm=True)
        else:
            for subword in key.split():
                if subword.lower() not in self.wv_glove.key_to_index:
                    logger.debug("can't vectorize {0!s}".format(key))
                    return None
            res = np.sum(
                [
                    self.wv_glove.get_vector(subword.lower(), norm=True)
                    for subword in key.split()
                ],
                axis=0,
            )
            norm = np.linalg.norm(res)
            return np.divide(res, norm)
