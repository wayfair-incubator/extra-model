"""simple vecotrizer class using prettrained vectors"""
import logging
import tempfile

import numpy as np
from gensim.models import KeyedVectors
from gensim.scripts.glove2word2vec import glove2word2vec
from gensim.test.utils import datapath, get_tmpfile

logger = logging.getLogger(__name__)


class vectorizer:
    """simple vectorizer class using pre-trained vectors"""

    def __init__(self, embedding_file, raw=True):
        """use the generic gensim vector embedding lookup
        currently using pretrained glove embeddings, but anything goes.
        parameters:
        embedding_file (string): pathname for the file that stores the word-mebedddings in gensim keyed-vectors format
        """
        if raw:
            self.wv_glove = KeyedVectors.load(embedding_file, mmap="r")
            # TODO: should this have True since help file says "If True - forget the original vectors and only keep the
            #  normalized ones = saves lots of memory!"
            self.wv_glove.init_sims()
        else:
            if embedding_file is None:
                glove_file = datapath("/app/glove.840B.300d.txt")
            else:
                glove_file = embedding_file
            tmp_file = get_tmpfile("test.txt")

            _ = glove2word2vec(glove_file, tmp_file)
            self.wv_glove = KeyedVectors.load_word2vec_format(tmp_file)
            self.wv_glove.init_sims()

    def get_vector(self, key):
        """return the vector embedding for a given word
        if no embedding is found for this word, check if it's a compound
        if it's a compound try to take the average embedding of the constitutent words
        if a that fails too, return None, downstream code will have to deal with the absence of an embedding
        (typical course of action is to ignore such a term)
        parameters:
        key (string): the word to be embedded
        returns:
        np.array : the embedding vector. Number of dimensions is set by the input file
        """
        if key.lower() in self.wv_glove.vocab:
            return self.wv_glove.word_vec(key.lower(), use_norm=True)
        else:
            for subword in key.split():
                if subword.lower() not in self.wv_glove.vocab:
                    logger.debug("can't vectorize {0!s}".format(key))
                    return None
            sum = np.sum(
                [
                    self.wv_glove.word_vec(subword.lower(), use_norm=True)
                    for subword in key.split()
                ],
                axis=0,
            )
            norm = np.linalg.norm(sum)
            return np.divide(sum, norm)
