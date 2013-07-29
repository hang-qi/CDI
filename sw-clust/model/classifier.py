import sys
sys.path.append('..')

import mpmath

from model import *
from model import probability
from preprocessing import vocabulary


class Classifier(object):
    def __init__(self, model_filename=None):
        if (model_filename is not None):
            self.load(model_filename)

    def setup(self, class_num, np1_voc, vp_voc, np2_voc, np1_prob, vp_prob, np2_prob, class_priors):
        self._class_num = class_num
        self._vocabularies = {
            WORD_TYPE_NP1: np1_voc,
            WORD_TYPE_VP: vp_voc,
            WORD_TYPE_NP2: np2_voc}
        self._probabilities = {
            WORD_TYPE_NP1: np1_prob,
            WORD_TYPE_VP: vp_prob,
            WORD_TYPE_NP2: np2_prob}
        self._class_priors = class_priors

    def build_from_corpus(self, corpus, class_list):
        # TODO:
        # prior from class list
        # prob from get distribution


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

    def predict(self, word_list_all_type, word_types):
        max_posterior = -1.0
        label = -1

        likelihoods = self._calculate_likelihoods_all_types(word_list_all_type, word_types)
        for class_index in range(0, self._class_num):
            # likelihood
            likelihood = 1.0
            for word_type in word_types:
                likelihood *= mpmath.mpf(likelihoods[word_type][class_index])

            posterior = likelihood * mpmath.mpf(self._class_priors[class_index])

            if posterior > max_posterior:
                max_posterior = posterior
                label = class_index
        return [label, max_posterior]

    def _calculate_likelihoods_all_types(self, word_list_all_type, word_types):
        """Calculate the likelihoods for all word types."""
        likelihoods_all_types = dict()
        for word_type in word_types:
            vocabulary = self._vocabularies[word_type]
            probability = self._probabilities[word_type]
            likelihoods_all_types[word_type] = self._calculate_likelihoods(word_list_all_type[word_type], vocabulary, probability)
        return likelihoods_all_types

    def _calculate_likelihoods(self, word_list, voc, voc_prob):
        """Calculate likelihood p(word_list|c) = \prod p(word|c) for all category c."""
        # Convert word into word ids
        word_ids = [voc.get_word_index(w) for w in word_list if w in voc]

        # calculate likelihood
        likelihoods = probability.Probability(1, self._class_num)
        for c in range(0, self._class_num):
            prob = 1
            for wid in word_ids:
                if wid != -1:
                    assert(voc_prob[wid, c] != 0)
                    prob *= voc_prob[wid, c]
            likelihoods[c] = prob
        return likelihoods


class OneTypeClassifier(Classifier):
    def __init__(self, model_filename=None):
        super(OneTypeClassifier, self).__init__(model_filename)

    def setup(self, class_num, vocabulary, likelihoods, class_priors):
        self._class_num = class_num
        self._vocabulary = vocabulary
        self._likelihoods = likelihoods
        self._class_priors = class_priors

    def load(self, classifier_model_file):
        # TODO:
        class_num = None
        vocabulary = None
        likelihoods = None
        class_priors = None
        self.setup(class_num, vocabulary, likelihoods, class_priors)

    def _calculate_likelihoods_all_types(self, word_list_all_type, word_types):
        """Calculate the likelihoods for all word types."""
        likelihoods_all_types = dict()
        for word_type in word_types:
            # Use the same vocabulary and distribution for all word types.
            likelihoods_all_types[word_type] = self._calculate_likelihoods(word_list_all_type[word_type], self._vocabulary, self._likelihoods)
        return likelihoods_all_types
