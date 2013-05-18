import sys
sys.path.append('..')
from vocabulary import triplet_vocabulary
from preprocessing import cleansing
import glob
from numpy.matlib import zeros
import numpy as np
from vocabulary import vocabulary


def generate_initial_npvp_voc(triplets_file_path):
    files = glob.glob(triplets_file_path)
    triplet_voc = generate_triplets_voc(files)
    triplet_voc.save('Triplet')
    print len(triplet_voc.np_list)
    print len(triplet_voc.vp_list)
    #triplet_initial_matrix = build_initial_triplets_cooccur_mat(triplet_voc, files)
    #np.savetxt('triplet_initial_matrix.txt', triplet_initial_matrix, fmt='%-7.2f')
    #triplet_matrix = morph_triplets_cooccur_mat(triplet_initial_matrix, np_matrix, vp_matrix)
    return


def learn_triplets_cooccur_mat(triplets_file_path):
    files = glob.glob(triplets_file_path)
    rm_np_voc = vocabulary.Vocabulary()
    rm_np_voc.load('../mat/np_to_delete.voc')
    rm_vp_voc = vocabulary.Vocabulary()
    rm_vp_voc.load('../mat/vp_to_delete.voc')
    np_voc = vocabulary.Vocabulary()
    vp_voc = vocabulary.Vocabulary()
    np_voc.load('../mat/np.voc')
    vp_voc.load('../mat/vp.voc')
    num_np = np_voc.size()
    num_vp = vp_voc.size()
    cooccur_mat = zeros([num_np, num_vp])
    for file_in in files:
        with open(file_in, 'r') as f:
            for line in f:
                if(line[0] != '<'):
                    line = line[:-2]
                    triplets = line.split('|')
                    np1 = triplets[0].split()
                    vp = triplets[1].split()
                    np2 = triplets[2].split()
                    for w in np2:
                        np1.append(w)
                    #for w in np1:
                    #    if rm_np_voc.contain(w):
                    np1 = [w for w in np1 if not rm_np_voc.contain(w)]
                    vp = [w for w in vp if not rm_vp_voc.contain(w)]
                    pairs = [(np_voc.get_word_index(u), vp_voc.get_word_index(v)) for u in np1 for v in vp]
                    for pair in pairs:
                        cooccur_mat[pair[0], pair[1]] += 1
    #np.save('cooccur_mat.npy', cooccur_mat)
    return cooccur_mat


def generate_triplets_voc(files):
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
    np_matrix = np.load('../mat/np_mat.npy')
    vp_matrix = np.load('../mat/vp_mat.npy')
    np_matrix = (np_matrix > 0.7) * np_matrix
    vp_matrix = (vp_matrix > 0.7) * vp_matrix
    return np.dot(np.dot(np_matrix, matrix), vp_matrix)
    #return np.dot(np_matrix, matrix) + np.dot(matrix, vp_matrix)


def main():
    cooccur_mat = learn_triplets_cooccur_mat('../triplet_files/*.txt')
    morphed_cooccur_mat = morph_triplets_cooccur_mat(cooccur_mat)
    np.savetxt('cooccur_mat_final.txt', morphed_cooccur_mat)
    return


if __name__ == '__main__':
    main()
