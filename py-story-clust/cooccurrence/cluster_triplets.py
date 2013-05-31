import sys
sys.path.append('..')
from vocabulary import triplet_vocabulary
from preprocessing import cleansing
import glob
from numpy.matlib import zeros
import numpy as np
from vocabulary import vocabulary


def learn_triplets_cooccur_mat(file_in):
    np_voc = vocabulary.Vocabulary()
    vp_voc = vocabulary.Vocabulary()
    np_voc.load('../mat/np1_co_mat.voc')
    vp_voc.load('../mat/np2_co_mat.voc')
    np1_all = vocabulary.Vocabulary()
    np2_all = vocabulary.Vocabulary()
    with open(file_in, 'r') as f:
        for line in f:
            if(line[0] != '<'):
                line = (line[:-2]).lower()
                triplets = line.split('|')
                np1 = cleansing.clean(triplets[0].split())
                vp = cleansing.clean(triplets[1].split())
                np2 = cleansing.clean(triplets[2].split())
                for w in np2:
                    vp.append(w)
                np1_new = [w for w in np1 if np_voc.contain(w)]
                np2_new = [w for w in vp if vp_voc.contain(w)]
                for w in np1_new:
                    np1_all.add(w)
                for w in np2_new:
                    np2_all.add(w)
        np1_matrix = np.load('../mat/np1_co_mat.npy')
        np2_matrix = np.load('../mat/np2_co_mat.npy')
        num_np1 = np1_all.size()
        num_np2 = np2_all.size()
        print num_np1
        print num_np2
        similarity_mat_np1 = zeros([num_np1, num_np1])
        similarity_mat_np2 = zeros([num_np2, num_np2])
        for i in range(num_np1):
            for j in range(num_np1):
                similarity_mat_np1[i, j] = np1_matrix[np_voc.get_word_index(np1_all.get_word(i)), np_voc.get_word_index(np1_all.get_word(j))]
        for i in range(num_np2):
            for j in range(num_np2):
                similarity_mat_np2[i, j] = np2_matrix[vp_voc.get_word_index(np2_all.get_word(i)), vp_voc.get_word_index(np2_all.get_word(j))]
    np.savetxt('../mat/similarity_mat_np1.txt', similarity_mat_np1)
    np.savetxt('../mat/similarity_mat_np2.txt', similarity_mat_np2)
    np1_all.save('../mat/similarity_np1.voc')
    np2_all.save('../mat/similarity_np2.voc')
    return


def main():
    file_in = '../1_6_Sports|Olympics.txt'
    learn_triplets_cooccur_mat(file_in)
    return


if __name__ == '__main__':
    main()
