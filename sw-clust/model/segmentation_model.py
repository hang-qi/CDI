# Provide the statistics for SW Process
from collections import defaultdict

import mpmath

from model import *


class SegmentationModel(object):
    def __init__(self, nodes, transprob, length_prior, seg_num_prior, classifier):
        self.all_nodes = nodes
        self.transition_prob = transprob
        self.length_prior = length_prior
        self.seg_num_prior = seg_num_prior
        self.classifier = classifier

        self._segment_classification_cache = dict()

    def calculate_Qe(self, left, right, context):
        right_node = self.all_nodes.nodes[right]
        if right_node.pronoun:
            # If the beginning of the right node is pronoun, turn on the edge
            return 1
        else:
            return 0.6

    def cooling_schedule(self, iteration_counter):
        starting_temperature = 1000
        period = 2
        step_size = 10

        temperature = starting_temperature - int(iteration_counter/period)*step_size
        if temperature <= 0:
            temperature = 0.1
        return temperature

    def target_evaluation_func(self, current_clustering, context=None):
        #print(current_labeling)
        energy = self.calculate_energy(current_clustering)
        temperature = 1000
        #print(energy)
        if context is not None:
            temperature = self.cooling_schedule(context.iteration_counter)
        return mpmath.exp(-(energy/temperature))

    def calculate_energy(self, current_clustering):
        """Energy Function: Category Posterior + Category Transition + Length Prior(Currently not included)"""
        energy = 0.0
        previous_category = -1

        for segment in current_clustering:
            # likelihood term (cache to prevent repeat computation)
            [category, prob] = self.classification(segment)

            if prob == 0:
                prob = 1e-100
            energy += -mpmath.log(prob)

            # transition prob term
            #if previous_category != -1:
            #    energy += -mpmath.log(self.transition_prob.get_value(category, previous_category) + 1e-100)
            previous_category = category

            # prior prob term
            energy += -mpmath.log(self.length_prior[len(segment) - 1])

        energy += -mpmath.log(self.seg_num_prior[len(current_clustering)])

        return energy

    def _segment_key(self, segment):
        l = list(segment)
        l.sort()
        return str(l)

    def classification(self, segment):
        key = self._segment_key(segment)
        if key not in self._segment_classification_cache:

            word_list_all_type = defaultdict(list)
            for i in segment:
                current_node = self.all_nodes.nodes[i]
                word_list_all_type[WORD_TYPE_NP1].extend(current_node.NP1)
                word_list_all_type[WORD_TYPE_VP].extend(current_node.VP)
                word_list_all_type[WORD_TYPE_NP2].extend(current_node.NP2)

            [category, prob] = self.classifier.classify(word_list_all_type)
            self._segment_classification_cache[key] = [category, prob]
        return self._segment_classification_cache[key]
