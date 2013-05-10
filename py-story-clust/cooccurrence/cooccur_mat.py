# Learn co-occurrence matrix from data

from numpy.matlib import zeros
import logging

from ..vocabulary import Vocabulary


def read_tpt(file):
    words = []
    # TODO: read tpt files into words

    # remove stop words

    return words


def build_vocabulary(tptFiles):
    words = []
    for f in tptFiles:
        words = read_tpt(f)

    voc = Vocabulary()
    for w in words:
        voc.insert(w)
    logging.debug("Vocabulary obtained: {0} words.".format(voc.size()))
    return voc


def fill_cooccurrence_matrix(matrix, vocabulary, tptFiles):
    for f in tptFiles:
        words = read_tpt(f)
    return


def learn_matrix(tptFiles):
    """Learn a word co-occurrence matrix from corpus."""

    # build vocabulary
    vocabulary = build_vocabulary(tptFiles)

    # build matrix
    num_words = vocabulary.size()
    matrix = zeros(num_words, num_words)

    # fill in matrix
    fill_cooccurrence_matrix(matrix, vocabulary, tptFiles)
    return matrix
