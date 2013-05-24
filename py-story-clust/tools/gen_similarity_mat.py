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
    distribution_matrix_dir = '../data/'    # the directory contain distribution matrices
    vocabularies_of_interest = ['../mat/np.voc', '../mat/vp.voc']
    generate_similarity_matrix(distribution_matrix_dir, vocabularies_of_interest)
    return


def generate_similarity_matrix(distribution_matrix_dir, vocabularies_of_interest):
    logging.basicConfig(level=logging.DEBUG)

    mat_filenames = glob.glob('{0}/*.npy'.format(distribution_matrix_dir))
    mat_filenames.sort()

    # list of pairs (vocabulary_filename, matrix_filename)
    files = []
    for mat_filename in mat_filenames:
        files.append((mat_filename.replace('.npy', '.voc'), mat_filename))
    logging.debug('Total # of sub matrices: {0}.'.format(len(files)))

    # load the full vocabulary
    full_vocab = vocabulary.Vocabulary()
    full_vocab.load('{0}/corpus_vocabulary.voc'.format(distribution_matrix_dir))
    logging.debug('Size of whole vocabulary: {0}.'.format(full_vocab.size()))

    # read the NP list and VP list
    for vocab_file in vocabularies_of_interest:
        logging.debug('Calculating similarity matrix for \'{0}\'...'.format(
            vocab_file))
        similarity_matrix = cooccur_mat.calculate_cooccur_mat_by_submatrices_and_save(
            vocab_file, full_vocab.size(), files)
    return


if __name__ == '__main__':
    main()
