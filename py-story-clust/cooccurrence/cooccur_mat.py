# Learn co-occurrence matrix from data

import logging
from numpy.matlib import zeros

from ..vocabulary import vocabulary
from ..preprocessing import word_morphy


def learn_matrix(tptFiles):
    """Learn a word co-occurrence matrix from corpus."""
    # build vocabulary
    vocab = build_vocabulary(tptFiles)

    # build matrix and fill in
    matrix = build_cooccur_matrix(vocab, tptFiles)
    return matrix


def build_vocabulary(tptFiles):
    words = []
    for f in tptFiles:
        words = read_tpt(f)

    voc = vocabulary.Vocabulary()
    for w in words:
        voc.insert(w)
    logging.debug("Vocabulary obtained: {0} words.".format(voc.size()))
    return voc


def build_cooccur_matrix(vocab, tptFiles):
    """Build co-occurrence matrix."""
    # TODO: fill co-occurrence matrix
    num_words = vocab.size()
    matrix = zeros(num_words, num_words)

    return matrix


def read_tpt(file):
    words = []
    # TODO: read tpt files into words

    for line in file:
        ws = line.split()

        # remove stop words

        # morph word to simple form
        ws = [word_morphy(w) for w in ws]
        words.extend(ws)

    return words
