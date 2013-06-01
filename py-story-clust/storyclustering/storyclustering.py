import sys
sys.path.append('..')
import glob
import numpy as np
from numpy.matlib import zeros
from math import sqrt
from preprocessing import cleansing
from vocabulary import vocabulary
from cooccurrence.cooccur_mat import CooccurMatrix
from vocabulary import triplet_vocabulary


def learn_story_distances(triplets_file_path):
    files = glob.glob(triplets_file_path)
    print len(files)
    file_num = len(files)
    np_voc = vocabulary.Vocabulary()
    np_voc.load('../mat/np1_co_mat.voc')
    np_num = np_voc.size()
    hist = zeros([file_num, np_num])
    count = 0
    for file_in in files:
        hist[count,:] = learn_story_histogram(file_in, np_voc)
        count += 1
    np.savetxt('../mat/histogram.txt', hist)
    np1_matrix = np.load('../mat/np1_co_mat.npy')
    dist = zeros([file_num, file_num])
    for i in range(file_num):
        for j in range(file_num):
            dif = hist[i,:] - hist[j,:]
            dist[i,j] = sqrt(np.dot(np.dot(dif, np1_matrix), dif.T))
    np.savetxt('../mat/distance.txt', dist)
    return


def learn_story_histogram(file_in, np_voc):
    np1_all = vocabulary.Vocabulary()
    np_num = np_voc.size()
    hist = zeros([1, np_num])
    with open(file_in, 'r') as f:
        for line in f:
            if(line[0] != '<'):
                line = (line[:-2]).lower()
                triplets = line.split('|')
                np1 = cleansing.clean(triplets[0].split())
                np1_new = [w for w in np1 if np_voc.contain(w)]
                for w in np1_new:
                    hist[0, np_voc.get_word_index(w)] += 1
    return hist


def main():
    learn_story_distances('../triplet_files/*.txt')
    return

if __name__ == '__main__':
    main()
