# Learn co-occurrence matrix from data

import sys
import glob
import codecs
import logging
import numpy as np
from numpy.matlib import zeros

from ..vocabulary import vocabulary


def learn_matrix(story_files):
    """Learn a word co-occurrence matrix from corpus."""
    # build vocabulary
    vocab = build_vocabulary(story_files)

    # build matrix and fill in
    matrix = build_cooccur_matrix(vocab, story_files)

    save_matrix(matrix)
    return matrix


def build_vocabulary(story_files):
    """Build a vocabulary from a set of given tpt files."""
    voc = vocabulary.Vocabulary()

    for story_file in story_files:
        words = read_story(story_file)
        for w in words:
            voc.add(w)

    logging.debug('Vocabulary obtained: {0} words.'.format(voc.size()))
    return voc


def build_cooccur_matrix(vocab, story_files):
    """Build co-occurrence matrix."""
    # TODO: fill in co-occurrence matrix
    num_words = vocab.size()
    co_matrix = zeros([num_words, num_words])

    for story_file in story_files:
        words = read_story(story_file)
        wordset = set(words)

        # frequencies = [ (u_id, v_id, p_u(v))]
        frequencies = [(vocab.get_word_index(u), vocab.get_word_index(v),
            words.count(u)*words.count(v)) for u in wordset for v in wordset]

        for element in frequencies:
            co_matrix[element[0], element[1]] += element[2]

    # normalize so that each row will sum to one.
    row_sums = co_matrix.sum(axis=1)
    co_matrix = co_matrix / row_sums[:]

    logging.debug('Print 15*15 sub matrix:')
    logging.debug(co_matrix[0:15, 0:15])
    logging.debug(co_matrix[np.ix_([1, 3, 5], [1, 3, 5])])
    return co_matrix

def save_matrix(matrix):
    # TODO: to be implemented.
    return


def read_story(filename):
    # TODO: read tpt files into words
    with codecs.open(filename, 'r', encoding='ISO-8859-1') as f:
        content = f.read()
    words = content.split()
    return words


def main():
    story_files = glob.glob(sys.argv[1])  # Interpret the wild-cards.
    learn_matrix(story_files)


if __name__ == '__main__':
    main()