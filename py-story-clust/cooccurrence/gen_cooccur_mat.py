# Script to generate co occurrence matrix.
# Usage: python gen_cooccur_mat.py

import sys
import glob
import logging
import codecs
import math
import numpy as np

sys.path.append('..')
from cooccurrence import cooccur_mat
from vocabulary import vocabulary


def main():
    logging.basicConfig(level=logging.DEBUG)

    mat_filenames = glob.glob('../data/*.npy')
    mat_filenames.sort()
    files = []
    for mat_filename in mat_filenames:
        files.append((mat_filename.replace('.npy', '.voc'), mat_filename))

    logging.debug('Total # of sub matrices: {0}.'.format(len(files)))

    # load the full vocabulary
    full_vocab = vocabulary.Vocabulary()
    full_vocab.load('vocabulary.voc')
    logging.debug('Size of whole vocabulary: {0}.'.format(full_vocab.size()))

    # read the NP list and VP list
    np_list = read_list('../Triplet.np_list')
    vp_list = read_list('../Triplet.vp_list')
    num_nps = len(np_list)
    num_vps = len(vp_list)

    co_mat_np = build_matrix(np_list, full_vocab.size(), files)
    cooccur_mat.save_matrix('np_mat.npy', co_mat_np)

    #co_mat_vp = build_matrix(vp_list, full_vocab.size(), files)
    #cooccur_mat.save_matrix('vp_mat.npy', co_mat_vp)
    return


def build_matrix(words, full_vocab_size, files):
    num_words = len(words)
    logging.debug('Total # of words: {0}.'.format(num_words))

    # Build contextual distribution matrix for NP.
    contextual_mat = np.zeros((num_words, full_vocab_size))

    num_it = 0
    for (voc_filename, mat_filename) in files:
        sub_vocab_list = read_list(voc_filename)
        sub_vocab_dict = {}     # maps word -> index
        for i in range(0, len(sub_vocab_list)):
            sub_vocab_dict[sub_vocab_list[i]] = i

        num_it += 1
        logging.debug('Iteration {0}, # of words in sub matrix: {1}'.format(
            num_it, len(sub_vocab_list)))

        # First read the vocabulary. Only load sub matrix if the matrix has the
        # distribution we want.
        has_target_word = False
        target_words_rows = []
        for i in range(0, num_words):
            try:
                # get the row id of the interested word in sub matrix.
                row_id = sub_vocab_dict[words[i]]
                target_words_rows.append(row_id)
                has_target_word = True
                pass
            except KeyError:
                target_words_rows.append(-1)

        # Don't load the sub matrix if no overlap word.
        if not has_target_word:
            logging.debug('Sub-matrix skipped.')
            continue

        sub_matrix = np.load(mat_filename)
        for i in range(0, num_words):
            row_id = target_words_rows[i]
            if row_id != -1:
                contextual_mat[i] = contextual_mat[i] + sub_matrix[row_id]

    # remove the words with no distribution information
    row_sums = contextual_mat.sum(axis=1)
    arrays_to_delte = []
    for i in range(0, num_words):
        if row_sums[i] == 0:
            arrays_to_delte.append(i)
            logging.warning('No contextual information for: ' + words[i])
    logging.warning('# of words deleted: ' + len(arrays_to_delte))

    # delete corresponding rows
    contextual_mat = np.delete(contextual_mat, arrays_to_delte, 0)

    # normalize
    row_sums = np.delete(row_sums, arrays_to_delte, 0)
    contextual_mat = contextual_mat / row_sums.reshape(-1, 1)

    # Build the similarity/ co-occurrence matrix.
    co_mat = cooccur_mat.calculate_cooccur_matrix(contextual_mat)

    logging.debug(contextual_mat)
    return co_mat


def read_list(filename):
    word_list = []
    with codecs.open(filename, 'r', encoding='ISO-8859-1') as f:
        for line in f:
            if len(line) > 0:
                word_list.append(line.strip('\n'))
    return word_list


if __name__ == '__main__':
    main()
