import sys
sys.path.append('..')

import mpmath

from model import *
from model import probability
from preprocessing import vocabulary


class Classifier(object):
    def __init__(self, class_num=0, np1_voc=None, vp_voc=None, np2_voc=None, np1_prob=None, vp_prob=None, np2_prob=None, class_prior_prob=None):
        self.setup(class_num, np1_voc, vp_voc, np2_voc, np1_prob, vp_prob, np2_prob, class_prior_prob)

    def setup(self, class_num, np1_voc, vp_voc, np2_voc, np1_prob, vp_prob, np2_prob, class_prior_prob):
        self._class_num = class_num
        self._vocabularies = [np1_voc, vp_voc, np2_voc]
        self._probabilities = [np1_prob, vp_prob, np2_prob]
        self._class_prior = class_prior_prob

    def load(self, classifier_model_file):
        """Load the classifier data."""
        with open(classifier_model_file, 'r') as f:
            # (1) Class Number
            class_num = int(f.readline()[:-1])

            # (2) Vocabularies
            # NP1
            np1_num = int(f.readline()[:-1])
            np1_voc = vocabulary.Vocabulary()
            for i in range(0, np1_num):
                np1_voc.add(f.readline()[:-1])
            f.readline()  # Blank line

            # VP
            vp_num = int(f.readline()[:-1])
            vp_voc = vocabulary.Vocabulary()
            for i in range(0, vp_num):
                vp_voc.add(f.readline()[:-1])
            f.readline()  # Blank line

            # NP2
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
                print('Class Number Does Not Match in File {0}'.format(classifier_model_file))
            f.readline()  # Blank line

            # (4) Vocabularies' Probability
            # NP1
            if np1_num == int(f.readline()[:-1]):
                np1_prob = probability.Probability(np1_num, class_num)
                for i in range(0, np1_num):
                    f.readline()  # class number
                    for j in range(0, class_num):
                        np1_prob.set_value(i, j, float(f.readline()[:-1]))
                    f.readline()  # Blank line
            else:
                print('NP1 Number Does Not Match in File {0}'.format(classifier_model_file))
            f.readline()  # Blank line
            # VP
            if vp_num == int(f.readline()[:-1]):
                vp_prob = probability.Probability(vp_num, class_num)
                for i in range(0, vp_num):
                    f.readline()  # class number
                    for j in range(0, class_num):
                        vp_prob.set_value(i, j, float(f.readline()[:-1]))
                    f.readline()  # Blank line
            else:
                print('VP Number Does Not Match in File {0}'.format(classifier_model_file))
            f.readline()  # Blank line
            # NP2
            if np2_num == int(f.readline()[:-1]):
                np2_prob = probability.Probability(np2_num, class_num)
                for i in range(0, np2_num):
                    f.readline()  # class number
                    for j in range(0, class_num):
                        np2_prob.set_value(i, j, float(f.readline()[:-1]))
                    f.readline()  # Blank line
            else:
                print('NP2 Number Does Not Match in File {0}'.format(classifier_model_file))
            f.readline()  # Blank line

            # (5) Classes' Transition Matrix
            #if class_num == int(f.readline()[:-1]):
            #    transition_prob = probability.Probability(class_num, class_num)  # current class given previous class
            #    for i in range(0, class_num):
            #        f.readline()  # Class number
            #        for j in range(0, class_num):
            #            transition_prob.set_value(i, j, float(f.readline()[:-1]))
            #        f.readline()  # Blank line
            #
            #    f.readline()
            #else:
            #    print('Class Number Does Not Match in File {0}'.format(classifier_model_file))

            # (6) Length Distribution
            #  Currently not calculated. TO be Added

        self.setup(class_num, np1_voc, vp_voc, np2_voc, np1_prob, vp_prob, np2_prob, class_prior_prob)

    def classify(self, word_list_all_type):
        [np1_cat_prob, vp_cat_prob, np2_cat_prob] = self._calculate_category_likelihood(word_list_all_type, WORD_TYPES)
        max_posterior = -1.0
        label = -1
        for class_index in range(0, self._class_num):
            # calculate posterior probability
            posterior = mpmath.mpf(np1_cat_prob[class_index]) * mpmath.mpf(vp_cat_prob[class_index]) * mpmath.mpf(np2_cat_prob[class_index])
            if posterior != 0:
                posterior /= mpmath.mpf(self._class_prior[class_index] * self._class_prior[class_index])

            if posterior > max_posterior:
                max_posterior = posterior
                label = class_index
        return [label, max_posterior]

    def _calculate_category_likelihood(self, word_list_all_type, word_types):
        cat_probs = []
        for word_type in word_types:
            current_type_prob = self._calculate_prob_cat_given_words(word_list_all_type[word_type], self._vocabularies[word_type], self._probabilities[word_type])
            cat_probs.append(current_type_prob)
        return cat_probs

    def _calculate_prob_cat_given_words(self, word_list, voc, voc_prob):
        word_id = []
        # Convert word into word ids by looking up dictionary
        for w in word_list:
            if voc.contain(w):
                word_id.append(voc.get_word_index(w))
            else:
                word_id.append(-1)

        # calculate probability
        prob_cats = probability.Probability(1, self._class_num)
        for i in range(0, self._class_num):
            prob = 1
            for wid in word_id:
                if wid != -1:
                    if voc_prob[wid, i] == 0:
                        print('Error')
                    prob *= voc_prob[wid, i]
            prob *= self._class_prior[i]
            prob_cats[i] = prob
        return prob_cats
