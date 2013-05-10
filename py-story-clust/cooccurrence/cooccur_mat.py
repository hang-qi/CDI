# Learn co-occurrence matrix from data

import logging
from numpy.matlib import zeros

from ..vocabulary import vocabulary
from ..preprocessing import cleansing


def learn_matrix(tpt_filenames):
    """Learn a word co-occurrence matrix from corpus."""
    # build vocabulary
    vocab = build_vocabulary(tpt_filenames)
    # build matrix and fill in
    matrix = build_cooccur_matrix(vocab, tpt_filenames)

    save_matrix(matrix)
    return matrix


def build_vocabulary(tpt_filenames):
    """Build a vocabulary from a set of given tpt files."""
    voc = vocabulary.Vocabulary()

    for f in tpt_filenames:
        words = []
        words = read_tpt(f)

        for w in words:
            voc.insert(w)

    logging.debug('Vocabulary obtained: {0} words.'.format(voc.size()))
    return voc


def build_cooccur_matrix(vocab, tpt_filenames):
    """Build co-occurrence matrix."""
    # TODO: fill in co-occurrence matrix
    num_words = vocab.size()
    matrix = zeros(num_words, num_words)

    return matrix


def save_matrix(matrix):
    # TODO: to be implemented.
    return


def read_tpt(filename):
    words = []
    # TODO: read tpt files into words
    f = open(filename)
    for line in f:
        # TODO: parse tag

        word_list = line.split()

        # remove stop words and morph word to its simplest form
        word_list = cleansing.remove_stopwords(word_list)
        word_list = [cleansing.morphy(w) for w in word_list]

        words.extend(word_list)

    return words
