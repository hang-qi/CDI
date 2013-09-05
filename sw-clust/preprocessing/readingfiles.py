# Defines the method to read in the test file for Story Segmentation
import glob
import sys
sys.path.append('..')
import os.path
import datetime

import cleansing
import vocabulary
from model.document import OrignalDocument
from model.sentence import Sentence
from model import probability

from scipy.stats import norm
import mpmath


def read_testing_file(filenameprefix):
    """Read the triplets files of the segments that correspond to the test file"""
    file_name = 'data/transformed_triplet_files/' + filenameprefix + '*.txt'
    files = glob.glob(file_name)
    files.sort()
    true_segment = []
    all_sentences = []
    line_count_total = 0
    for segments_file in files:
        # Delete the teaser files
        if (segments_file.split('/')[-1].split('_')[-1].split('|')[0].split(':')[-1] == 'Teaser'
           or segments_file.split('/')[-1].split('_')[-1].split('.')[0] == 'NULL'):
            continue
        line_count = -1
        current_seg_sentences = []
        with open(segments_file, 'r') as f:
            for line in f:
                if(line[0] != '<'):
                    line_count += 1
                    line = (line[:-2]).lower()
                    triplets = line.split('|')

                    np1 = triplets[0].split()
                    if np1 != [] and _is_pronoun(np1[0]):
                        pronoun_flag = True
                    else:
                        pronoun_flag = False
                    np1 = cleansing.clean(triplets[0].split())
                    vp = cleansing.clean(triplets[1].split())
                    np2 = cleansing.clean(triplets[2].split())
                    current_seg_sentences.append(Sentence(np1, vp, np2, pronoun_flag))

        # Only keep segments longer than 5 sentences
        segment_length = len(current_seg_sentences)
        if (segment_length > 5):
            seg = [(sid + line_count_total) for sid in range(0, segment_length)]
            true_segment.append(set(seg))
            all_sentences.extend(current_seg_sentences)
            line_count_total += segment_length
    return [all_sentences, true_segment]


def _is_pronoun(word):
    return word in _is_pronoun.pronoun_set
_is_pronoun.pronoun_set = {'they', 'he', 'she', 'his', 'her', 'they', 'their', 'those', 'that', 'these', 'which', 'its'}


def load_model_parameters(training_file_in):
    [class_num, np1_voc, vp_voc, np2_voc, np1_prob, vp_prob, np2_prob, class_prior_prob, transition_prob] = _read_training_classification_data(training_file_in)
    # Add the Length Priors
    length_prior = []
    prior_dist_range = 500
    for i in range(0, prior_dist_range):
        j = i + 1.0
        length_prior.append(mpmath.mpf(10.0*norm(20, 15).pdf(j) + 5.0*norm(5, 15).pdf(j)))
        #length_prior.append(1)\

    # Norm the probability
    length_prior = _prob_normalization(length_prior)

    # Add the Total Segment Number Prior
    seg_num_prior = []
    for i in range(0, prior_dist_range):
        seg_num_prior.append(mpmath.mpf(norm(25.0, 10.0).pdf(i)))
    seg_num_prior = _prob_normalization(seg_num_prior)

    return [transition_prob, length_prior, seg_num_prior]


def _read_training_classification_data(file_in):
    """Read the data for classification"""
    with open(file_in, 'r') as f:
        # (1) Class Number
        class_num = int(f.readline()[:-1])
        # (2) Vocabularies
        #     NP1
        np1_num = int(f.readline()[:-1])
        np1_voc = vocabulary.Vocabulary()
        for i in range(0, np1_num):
            np1_voc.add(f.readline()[:-1])
        f.readline()  # Blank line
        #     VP
        vp_num = int(f.readline()[:-1])
        vp_voc = vocabulary.Vocabulary()
        for i in range(0, vp_num):
            vp_voc.add(f.readline()[:-1])
        f.readline()  # Blank line
        #     NP2
        np2_num = int(f.readline()[:-1])
        np2_voc = vocabulary.Vocabulary()
        for i in range(0, np2_num):
            np2_voc.add(f.readline()[:-1])
        f.readline()  # Blank line
        # (3) Priors for classes
        if class_num == int(f.readline()[:-1]):
            class_prior_prob = probability.Probability(1, class_num)
            for i in range(0, class_num):
                class_prior_prob.set_value(0, i, float(f.readline()[:-1]))
        else:
            print('Class Number Does Not Match in File {0}'.format(file_in))
        f.readline()  # Blank line
        # (4) Vocabularies' Probability
        #     NP1
        if np1_num == int(f.readline()[:-1]):
            np1_prob = probability.Probability(np1_num, class_num)
            for i in range(0, np1_num):
                f.readline()  # class number
                for j in range(0, class_num):
                    np1_prob.set_value(i, j, float(f.readline()[:-1]))
                f.readline()  # Blank line
        else:
            print('NP1 Number Does Not Match in File {0}'.format(file_in))
        f.readline()  # Blank line
        #     VP
        if vp_num == int(f.readline()[:-1]):
            vp_prob = probability.Probability(vp_num, class_num)
            for i in range(0, vp_num):
                f.readline()  # class number
                for j in range(0, class_num):
                    vp_prob.set_value(i, j, float(f.readline()[:-1]))
                f.readline()  # Blank line
        else:
            print('VP Number Does Not Match in File {0}'.format(file_in))
        f.readline()  # Blank line
        #     NP2
        if np2_num == int(f.readline()[:-1]):
            np2_prob = probability.Probability(np2_num, class_num)
            for i in range(0, np2_num):
                f.readline()  # class number
                for j in range(0, class_num):
                    np2_prob.set_value(i, j, float(f.readline()[:-1]))
                f.readline()  # Blank line
        else:
            print('NP2 Number Does Not Match in File {0}'.format(file_in))
        f.readline()  # Blank line
        # (5) Classes' Transition Matrix
        if class_num == int(f.readline()[:-1]):
            transition_prob = probability.Probability(class_num, class_num)  # current class given previous class
            for i in range(0, class_num):
                f.readline()  # Class number
                for j in range(0, class_num):
                    transition_prob.set_value(i, j, float(f.readline()[:-1]))
                f.readline()  # Blank line

            f.readline()
        else:
            print('Class Number Does Not Match in File {0}'.format(file_in))
        # (6) Length Distribution
        #  Currently not calculated. TO be Added
    return [class_num, np1_voc, vp_voc, np2_voc, np1_prob, vp_prob, np2_prob, class_prior_prob, transition_prob]


def read_training_clusters(file_in):
    # Todo: Add the functions to read the clusters here
    return


def _prob_normalization(dist):
    dist_sum = sum(dist)
    for i in range(0, len(dist)):
        dist[i] /= dist_sum
    return dist


def read_triplet_file(triplet_filename, use_ocr=False):
    ocr_file = None
    np1_words = []
    vp_words = []
    np2_words = []
    count = 0
    with open(triplet_filename, 'r') as f:
        for line in f:
            if(line[0] != '<'):
                count += 1
                line = (line[:-2]).lower()
                triplets = line.split('|')
                np1_words.extend(cleansing.clean(triplets[0].split()))
                if len(triplets) == 3:
                    vp_words.extend(cleansing.clean(triplets[1].split()))
                    np2_words.extend(cleansing.clean(triplets[2].split()))
    #if count < 10:
    #    return OrignalDocument('', '', [], [], [], [])
    ocr_words = []
    if use_ocr:
        #name_tmp = triplet_filename.split('&')[-2] + '_' + triplet_filename.split('&')[-1].replace('.txt', '.ocr')
        #ocr_file = 'data/ocr_result_080819-081015/' + name_tmp.lower()
        name_tmp = triplet_filename[:-4].split('/')[-1]
        ocr_file = 'data/ocr_result_ori/' + name_tmp.lower()
        if os.path.exists(ocr_file):
            with open(ocr_file, 'r') as f:
                for line in f:
                    if(line[0] != '<'):
                        line = (line[:-2]).lower()
                        ocr_words.extend(cleansing.clean(line.split()))

    #timestamp = datetime.datetime.strptime((triplet_filename.split('/')[-1]).split('&')[1].split('.')[0], '%Y%m%d%H%M%S')
    #name_tmp = triplet_filename.split('/')[-1][:-4].split('&')
    #filename = name_tmp[1] + '&' + name_tmp[2]
    timestamp = datetime.datetime.strptime((triplet_filename.split('/')[-1]).split('_')[0].split('.')[0], '%Y%m%d%H%M%S')
    filename = triplet_filename.split('/')[-1][:-4]
    return OrignalDocument(filename, timestamp, np1_words, vp_words, np2_words, ocr_words)
