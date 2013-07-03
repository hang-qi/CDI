# Provide the statistics for SW Process
import sys
sys.path.append('..')
import math
from model.nodes import Node, Nodes


class Statistics(object):
    def __init__(self, nodes, cnum, np1voc, vpvoc, np2voc, np1prob, vpprob, np2prob, classpriorprob, transprob):
        self.all_nodes = nodes
        self.class_num = c_num
        self.np1_voc = np1voc
        self.np1_prob = np1prob
        self.vp_voc = vpvoc
        self.vp_prob = vpprob
        self.np2_voc = np2voc
        self.np2_prob = np2prob
        self.transition_prob = transprob

    def calculate_Qe(left, right):
        right_node = self.all_nodes[right]
        if right_node.pronoun:  # If the beginning of the right node is pronoun, turn on the edge
            return 1
        else:  # Return the probability
            return 0.6

    def target_evaluation_func(current_labeling):
        return math.exp(-calculate_energy(current_labeling))

    def calculate_energy(current_labeling):
        """Energy Function: Category Posterior + Category Transition + Length Prior(Currently not included)"""
        energy = 0
        if len(current_labeling) == self.all_nodes.node_num:
            current_seg = []
            previous_seg_cat = -1
            prev_label = -1
            for i in range(0, self.all_nodes.node_num):
                if current_labeling[i] != prev_label:
                    if prev_label != -1:  # Not the first segment
                        [current_seg_cat, prob] = classification(current_seg)
                        energy += math.log(prob)
                        if previous_seg_cat != -1:  # Add the transition prob
                            energy += math.log(self.transition_prob.get_value(current_seg_cat, previous_seg_cat))
                        previous_seg_cat = current_seg_cat
                        current_seg = []  # clear the current segment
                current_seg.append(i)
                prev_label = current_labeling[i]
        else:
            print('Error: Node Number Does Not Match')
        energy = -energy
        return energy

    def classification(current_seg):
        for i in current_seg:
            
        return [label, prob]
