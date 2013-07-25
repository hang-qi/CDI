# Defines the method to read in the test file for Story Segmentation
import glob
import sys
sys.path.append('..')

import cleansing
import vocabulary
from model.nodes import Node, Nodes
from model import probability

from scipy.stats import norm
import mpmath


def read_testing_file(filenameprefix):
    """Read the triplets files of the segments that correspond to the test file"""
    file_name = 'triplet_files/' + filenameprefix + '*.txt'
    files = glob.glob(file_name)
    files.sort()
    true_segment = []
    all_nodes = Nodes()
    line_count = -1
    for segments_file in files:
        with open(segments_file, 'r') as f:
            current_seg = []
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
                    current_node = Node()
                    current_node.set_node(np1, vp, np2, pronoun_flag)
                    all_nodes.add_node(current_node)
                    current_seg.append(line_count)
        true_segment.append(set(current_seg))
    return [all_nodes, true_segment]


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
        length_prior.append(mpmath.mpf(10.0*norm(15, 15).pdf(j) + 5.0*norm(2, 20).pdf(j)))
        #length_prior.append(1)\

    # Norm the probability
    length_prior = _prob_normalization(length_prior)

    # Add the Total Segment Number Prior
    seg_num_prior = []
    for i in range(0, prior_dist_range):
        seg_num_prior.append(mpmath.mpf(norm(30.0, 20.0).pdf(i)))
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
