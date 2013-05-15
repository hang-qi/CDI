from vocabulary import triplet_vocabulary
from preprocessing import cleansing
import glob
from numpy.matlib import zeros
import numpy as np


def learn_triplets_cooccur_mat(triplets_file_path):
    files = glob.glob(triplets_file_path)
    triplet_voc = generate_triplets_matrix(files)
    triplet_voc.save('Triplet')
    print len(triplet_voc.np_list)
    print len(triplet_voc.vp_list)
    triplet_initial_matrix = build_initial_triplets_cooccur_mat(triplet_voc, files)
    np.savetxt('triplet_initial_matrix.txt', triplet_initial_matrix, fmt='%-7.2f')
    #triplet_matrix = morph_triplets_cooccur_mat(triplet_initial_matrix)
    return


def generate_triplets_matrix(files):
    triplet_voc = triplet_vocabulary.TripletVocabulary()
    for file_in in files:
        with open(file_in, 'r') as f:
            for line in f:
                if(line[0] != '<'):
                    line = line[:-2]
                    triplets = line.split('|')
                    # remove stop words and save NP1, NP2 -> np, VP -> vp
                    np1 = cleansing.clean(triplets[0].split())
                    for w in np1:
                        triplet_voc.add_np(w)
                    vp = cleansing.clean(triplets[1].split())
                    for w in vp:
                        triplet_voc.add_vp(w)
                    np2 = cleansing.clean(triplets[2].split())
                    for w in np2:
                        triplet_voc.add_np(w)
    return triplet_voc


def build_initial_triplets_cooccur_mat(triplet_voc, files):
    num_np = triplet_voc.np_size()
    num_vp = triplet_voc.vp_size()
    cooccur_mat = zeros([num_np, num_vp])
    for file_in in files:
        with open(file_in, 'r') as f:
            for line in f:
                if(line[0] != '<'):
                    line = line[:-2]
                    triplets = line.split('|')
                    np1 = cleansing.clean(triplets[0].split())
                    vp = cleansing.clean(triplets[1].split())
                    np2 = cleansing.clean(triplets[2].split())
                    for w in np2:
                        np1.append(w)
                    pairs = [(triplet_voc.np_index(u), triplet_voc.vp_index(v)) for u in np1 for v in vp]
                    for pair in pairs:
                        cooccur_mat[pair[0], pair[1]] += 1
    return cooccur_mat


def morph_triplets_cooccur_mat(matrix):
    # Multiply the learned coefficient matrix
    # To be implemented
    return


def main():
    learn_triplets_cooccur_mat('triplet_files/*.txt')
    return


if __name__ == '__main__':
    main()
