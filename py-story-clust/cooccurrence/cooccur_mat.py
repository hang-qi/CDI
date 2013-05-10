# Learn co-occurrence matrix from data

from numpy.matlib import zeros


def read_tpt(file):
    words = []
    # TODO: read tpt files into words

    # remove stop words

    return words


def build_vocabulary(tptFiles):
    words = []
    for f in tptFiles:
        words = read_tpt(f)

    words_dict = dict()
    vocabulary = []
    for w in words:
        if w not in words_dict:
            vocabulary.insert(w)
            words_dict[w] = len(vocabulary) - 1
    return words_dict


def fill_cooccurrence_matrix(matrix, tptFiles):
    pass


def learn_matrix(tptFiles):
    """Learn a word co-occurrence matrix from corpus."""

    # build vocabulary
    word_dict = build_vocabulary(tptFiles)

    # build matrix
    num_words = len(word_dict)
    matrix = zeros(num_words, num_words)

    # fill in matrix
    fill_cooccurrence_matrix(matrix, tptFiles)
    return matrix
