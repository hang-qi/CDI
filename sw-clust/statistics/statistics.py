# Provide the statistics for SW Process
import sys
sys.path.append('..')
import math
from model.nodes import Node, Nodes
from model import probability


class Statistics(object):
    def __init__(self, nodes, cnum, np1voc, vpvoc, np2voc, np1prob, vpprob, np2prob, classpriorprob, transprob):
        self.all_nodes = nodes
        self.class_num = cnum
        self.np1_voc = np1voc
        self.np1_prob = np1prob
        self.vp_voc = vpvoc
        self.vp_prob = vpprob
        self.np2_voc = np2voc
        self.np2_prob = np2prob
        self.transition_prob = transprob
        self.class_prior = classpriorprob

    def calculate_Qe(self, left, right, context):
        right_node = self.all_nodes.nodes[right]
        if right_node.pronoun:  # If the beginning of the right node is pronoun, turn on the edge
            return 1
        else:  # Return the probability
            count = int(context.iteration_counter/100)
            if count > 7:
                count = 7
            return 0.2 + 0.1*count

    def target_evaluation_func(self, current_labeling):
        #print(current_labeling)
        energy = self.calculate_energy(current_labeling)
        #print(energy)
        energy /= 1000
        return math.exp(-energy)

    def calculate_energy(self, current_labeling):
        """Energy Function: Category Posterior + Category Transition + Length Prior(Currently not included)"""
        energy = 0
        if len(current_labeling) == self.all_nodes.node_num:
            current_seg = []
            previous_seg_cat = -1
            prev_label = -1
            for i in range(0, self.all_nodes.node_num):
                if current_labeling[i] != prev_label:
                    if prev_label != -1:  # Not the first segment
                        [current_seg_cat, prob] = self.classification(current_seg)
                        # print('Classification Result: Category {0}, Probability {1}'.format(current_seg_cat, prob))
                        energy += math.log(prob)
                        if previous_seg_cat != -1:  # Add the transition prob
                            energy += math.log(self.transition_prob.get_value(current_seg_cat, previous_seg_cat) + 1e-100)
                        previous_seg_cat = current_seg_cat
                        current_seg = []  # clear the current segment
                    prev_label = current_labeling[i]
                current_seg.append(i)
        else:
            print('Error: Node Number Does Not Match')
        energy = -energy
        return energy

    def classification(self, current_seg):
        #np1_set = []
        #vp_set = []
        #np2_set = []
        #for i in current_seg:
        #    current_node = self.all_nodes.nodes[i]
        #    for w in current_node.NP1:
        #        np1_set.append(w)
        #    for w in current_node.VP:
        #        vp_set.append(w)
        #    for w in current_node.NP2:
        #        np2_set.append(w)
        #np1_cat_prob = self.calculate_prob_CatGivenWord(np1_set, self.np1_voc, self.np1_prob)
        #vp_cat_prob = self.calculate_prob_CatGivenWord(vp_set, self.vp_voc, self.vp_prob)
        #np2_cat_prob = self.calculate_prob_CatGivenWord(np2_set, self.np2_voc, self.np2_prob)
        [np1_cat_prob, vp_cat_prob, np2_cat_prob] = self.calculate_prob(current_seg)
        max_prob = -1
        label = -1
        for i in range(0, self.class_num):
            prob = np1_cat_prob.get_value(0, i) * vp_cat_prob.get_value(0, i) * np2_cat_prob.get_value(0, i)
            if prob != 0:
                prob /= (self.class_prior.get_value(0, i) * self.class_prior.get_value(0, i))
            if prob > max_prob:
                max_prob = prob
                label = i
        return [label, max_prob]

    def calculate_prob(self, current_seg):
        np1_cat_prob = probability.Probability(1, self.class_num)
        vp_cat_prob = probability.Probability(1, self.class_num)
        np2_cat_prob = probability.Probability(1, self.class_num)
        for i in range(0, self.class_num):
            prob_np1 = 1
            prob_vp = 1
            prob_np2 = 1
            for j in current_seg:
                prob_np1 *= self.all_nodes.nodes[j].np1_probgivencat.get_value(0, i)
                prob_vp *= self.all_nodes.nodes[j].vp_probgivencat.get_value(0, i)
                prob_np2 *= self.all_nodes.nodes[j].np2_probgivencat.get_value(0, i)
            prior = self.class_prior.get_value(0, i)
            prob_np1 *= prior
            prob_vp *= prior
            prob_np2 *= prior
            np1_cat_prob.set_value(0, i, prob_np1)
            vp_cat_prob.set_value(0, i, prob_vp)
            np2_cat_prob.set_value(0, i, prob_np2)
        return [np1_cat_prob, vp_cat_prob, np2_cat_prob]

    def calculate_prob_CatGivenWord(self, words, voc, voc_prob):
        word_id = []
        for w in words:
            if voc.contain(w):
                word_id.append(voc.get_word_index(w))
            else:
                word_id.append(-1)
        prob_all_cats = probability.Probability(1, self.class_num)
        for i in range(0, self.class_num):
            prob = 1
            for wid in word_id:
                if wid != -1:
                    if voc_prob.get_value(wid, i) == 0:
                        print('Error')
                    prob *= voc_prob.get_value(wid, i)
            prob *= self.class_prior.get_value(0, i)
            prob_all_cats.set_value(0, i, prob)
        return prob_all_cats
