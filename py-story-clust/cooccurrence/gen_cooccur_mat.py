# Script to generate co occurrence matrix.
# Usage: python gen_cooccur_mat.py files
#        e.g. python gen_cooccur_mat.py /*.txt

import sys
import glob
import logging
import math

sys.path.append('..')
from cooccurrence import cooccur_mat
from vocabulary import vocabulary


def main():
    logging.basicConfig(level=logging.DEBUG)


    ## For small dataset, whole matrix is to be generated in memory.
    # story_files = sys.argv[1:]
    # cooccur_mat.learn_matrix(story_files)

    # For large dataset, we calculate sub distribution matrices separately,
    # and then generate co-occurrence matrix for subset of vocabulary.
    story_files = glob.glob('/dataset/08cleaned/2008-0[567]*.txt')
    story_files.sort()
    logging.debug('Totol # of files: {0}'.format(len(story_files)))

    # Build whole vocab
    whole_vocab = cooccur_mat.build_vocabulary(story_files)
    whole_vocab.save('vocabulary.voc')

    # load the full vocabulary
    #whole_vocab = vocabulary.Vocabulary()
    #whole_vocab.load('vocabulary.voc')
    logging.debug('Size of whole vocabulary: {0}.'.format(whole_vocab.size()))

    num_files = len(story_files)
    batch_size = 100
    num_batches = int(math.ceil(num_files/batch_size))
    for b in range(0, num_batches):
        start = b * batch_size
        stop = (b+1) * batch_size

        logging.debug(
            'Batch {0} / {1} : [{2} : {3}]...'.format(b, num_batches, start, stop))
        cooccur_mat.build_sub_contextual_matrix_and_save(
            whole_vocab, story_files[start:stop], b)

if __name__ == '__main__':
    main()
