import mpmath

from model import *
from model import probability


class Classifier(object):
    def __init__(self, class_num, np1_voc, vp_voc, np2_voc, np1_prob, vp_prob, np2_prob, class_prior_prob):
        self._class_num = class_num
        self._vocabularies = [np1_voc, vp_voc, np2_voc]
        self._probabilities = [np1_prob, vp_prob, np2_prob]
        self._class_prior = class_prior_prob

    def classify(self, word_list_all_type):
        [np1_cat_prob, vp_cat_prob, np2_cat_prob] = self._calculate_category_likelihood(word_list_all_type, WORD_TYPES)
        max_posterior = -1.0
        label = -1
        for class_index in range(0, self._class_num):
            # calculate posterior probability
            posterior = mpmath.mpf(np1_cat_prob[class_index]) * mpmath.mpf(vp_cat_prob[class_index]) * mpmath.mpf(np2_cat_prob[class_index])
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
        prob_cats = probability.Probability(1, self.class_num)
        for i in range(0, self.class_num):
            prob = 1
            for wid in word_id:
                if wid != -1:
                    if voc_prob[wid, i] == 0:
                        print('Error')
                    prob *= voc_prob[wid, i]
            prob *= self._class_prior[i]
            prob_cats[i] = prob
        return prob_cats
