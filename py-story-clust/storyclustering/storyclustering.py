import sys
sys.path.append('..')
import glob
import numpy as np
from math import sqrt
from preprocessing import cleansing
from cooccurrence.cooccur_mat import CooccurMatrix
import codecs


def learn_story_distances(triplets_file_path, co_mat_file, use_similarity=True, min_similarity=None, output_file=False):
    # Load learned similarity matrix.
    learned_co_mat = CooccurMatrix()
    learned_co_mat.load(co_mat_file)
    np_voc = learned_co_mat.vocabulary
    np1_matrix = learned_co_mat.matrix
    if min_similarity is not None:
        np1_matrix = (np1_matrix >= 0.8) * np1_matrix

    files = glob.glob(triplets_file_path)
    files.sort()
    print len(files)
    file_num = len(files)

    # Calculate word histogram for each story.
    np_num = np_voc.size()
    hist = np.zeros([file_num, np_num])
    count = 0
    for file_in in files:
        (h, wordlist) = learn_story_histogram(file_in, np_voc)
        hist[count, :] = h
        count += 1

    # Calculate pair-wise distance between stories.
    dist = np.zeros([file_num, file_num])
    for i in range(file_num):
        for j in range(file_num):
            dif = hist[i, :] - hist[j, :]
            if use_similarity:
                sq = np.dot(np.dot(dif, np1_matrix), dif.T)
                if (sq < 0):
                    sq = 0
                dist[i, j] = sqrt(sq)
            else:
                dist[i, j] = sqrt(np.dot(dif, dif.T))

    labels = []
    for filename in files:
        labels.append(filename.split('/')[-1][:-4])

    if output_file:
        np.savetxt('../mat/histogram.txt', hist)
        np.savetxt('../mat/distance.txt', dist)
        with codecs.open('../mat/filename.txt', "w", encoding='ISO-8859-1') as f:
            for l in labels:
                f.writelines(l + '\n')
    return (dist, labels)


def learn_story_histogram(file_in, words_voc, word_type='ALL', ocr_file=None):
    """word_type = 'NP1', 'VP', 'NP2', 'ALL'"""
    words_voc_num = words_voc.size()
    hist = np.zeros([1, words_voc_num])
    document = []

    with open(file_in, 'r') as f:
        for line in f:
            if(line[0] != '<'):
                line = (line[:-2]).lower()
                words = []
                triplets = line.split('|')
                if (word_type == 'NP1' or word_type == 'ALL'):
                    words.extend(cleansing.clean(triplets[0].split()))
                if (word_type == 'VP' or word_type == 'ALL'):
                    words.extend(cleansing.clean(triplets[1].split()))
                if (word_type == 'NP2' or word_type == 'ALL'):
                    words.extend(cleansing.clean(triplets[2].split()))

                words_new = [w for w in words if words_voc.contain(w)]
                document.extend(words_new)
                for w in words_new:
                    hist[0, words_voc.get_word_index(w)] += 1

    # Read OCR file and combine into histogram if provided.
    ocr_words = []
    if ocr_file is not None:
        # TODO:
        # read ocr file
        # combine OCR into histogram
        # each word count 2
        # fill ocr_words
        with open(ocr_file, 'r') as f:
            for line in f:
                if(line[0] != '<'):
                    line = (line[:-2]).lower()
                    ocr_words.extend(cleansing.clean(line.split()))
                    ocr_words_new = [w for w in ocr_words if words_voc.contain(w)]
                    document.extend(ocr_words_new)
                    for w in ocr_words_new:
                        hist[0, words_voc.get_word_index(w)] += 1

    # Normalize.
    sum_hist = hist.sum()
    if sum_hist != 0:
        hist = hist / sum_hist
        try:
            assert(hist.sum() > 0.9 and hist.sum() < 1.1)
        except AssertionError:
            print(hist)
            print(hist.sum())
            raise
    return (hist, document, ocr_words)


def main():
    learn_story_distances('../triplet_files/*.txt', '../mat/np1_co_mat', output_file=True)
    return

if __name__ == '__main__':
    main()
