import sys
sys.path.append('..')
import glob
import numpy as np
from numpy.matlib import zeros

from preprocessing import cleansing
from vocabulary import vocabulary
from cooccurrence.cooccur_mat import CooccurMatrix
from vocabulary import triplet_vocabulary


def learn_triplets_cooccur_mat(file_in):
    np_voc = vocabulary.Vocabulary()
    np_voc.load('../mat/np1_co_mat.voc')
    np1_matrix = np.load('../mat/np1_co_mat.npy')

    np1_all = vocabulary.Vocabulary()
    with open(file_in, 'r') as f:
        for line in f:
            if(line[0] != '<'):
                line = (line[:-2]).lower()
                triplets = line.split('|')
                np1 = cleansing.clean(triplets[0].split())

                # Delete words not in the similarity vocabulary.
                np1_new = [w for w in np1 if np_voc.contain(w)]
                for w in np1_new:
                    np1_all.add(w)

    num_np1 = np1_all.size()
    similarity_mat_np1 = zeros([num_np1, num_np1])
    for i in range(num_np1):
        for j in range(num_np1):
            similarity_mat_np1[i, j] = np1_matrix[np_voc.get_word_index(np1_all.get_word(i)), np_voc.get_word_index(np1_all.get_word(j))]

    return CooccurMatrix(similarity_mat_np1, np1_all)


def main():
    cooccur_matrix = learn_triplets_cooccur_mat(file_in)
    return

if __name__ == '__main__':
    main()
