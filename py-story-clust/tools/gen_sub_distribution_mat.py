# Script to generate sub contextual distribution matrix.
# Usage: python gen_sub_distribution_mat.py

import sys
import glob
import logging
import math

sys.path.append('..')
from cooccurrence import cooccur_mat
from vocabulary import vocabulary


def main():
    corpus = '/dataset/08cleaned/2008-0[567]*.txt'  # corpus used to build the matrix
    output_dir = '../data/'   # directory to store the distribution matrices

    generate_sub_distribution_matrix(corpus, output_dir)
    return


def generate_sub_distribution_matrix(corpus_files, output_dir):
    logging.basicConfig(level=logging.DEBUG)

    # For large dataset, we calculate sub distribution matrices separately,
    # and then generate co-occurrence matrix for subset of vocabulary.
    story_files = glob.glob(corpus_files)
    story_files.sort()
    logging.debug('Total # of files: {0}'.format(len(story_files)))

    # Build full vocabulary
    full_vocab = cooccur_mat.build_vocabulary(story_files)
    full_vocab.save('{0}/corpus_vocabulary.voc'.format(output_dir))

    logging.debug('Size of whole vocabulary: {0}.'.format(full_vocab.size()))

    num_files = len(story_files)
    batch_size = 100
    num_batches = int(math.ceil(num_files/batch_size))
    for b in range(0, num_batches):
        start = b * batch_size
        stop = (b+1) * batch_size

        vocabulary_filename = '{0}/sub_matrix_{1}.voc'.format(output_dir, b)
        matrix_filename = '{0}/sub_matrix_{1}.npy'.format(output_dir, b)

        logging.debug(
            'Batch {0} / {1} : [{2} : {3}]...'.format(b, num_batches, start, stop))
        cooccur_mat.build_sub_contextual_matrix_and_save(
            full_vocab, story_files[start:stop], vocabulary_filename, matrix_filename)


if __name__ == '__main__':
    main()
