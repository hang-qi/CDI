# Defines the nodes in the graph
import sys
sys.path.append('..')
from preprocessing.vocabulary import Vocabulary
import probability


class Node(object):
    def __init__(self):
        self.NP1 = []
        self.VP = []
        self.NP2 = []
        self.pronoun = False
        self.np1_probgivencat = None
        self.vp_probgivencat = None
        self.np2_probgivencat = None

    def set_node(self, np1, vp, np2, ispronounflag):
        self.NP1 = np1
        self.VP = vp
        self.NP2 = np2
        self.pronoun = ispronounflag


class Nodes(object):
    def __init__(self):
        self.node_num = 0
        self.nodes = []

    def add_node(self, newnode):
        self.nodes.append(newnode)
        self.node_num += 1

    def set_nodes_prob(self, class_num, np1_voc, vp_voc, np2_voc, np1_prob, vp_prob, np2_prob):
        for i in range(0, self.node_num):
            self.nodes[i].np1_probgivencat = self.cal_prob(self.nodes[i].NP1, np1_voc, np1_prob, class_num)
            self.nodes[i].vp_probgivencat = self.cal_prob(self.nodes[i].VP, vp_voc, vp_prob, class_num)
            self.nodes[i].np2_probgivencat = self.cal_prob(self.nodes[i].NP2, np2_voc, np2_prob, class_num)

    def cal_prob(self, words, voc, voc_prob, class_num):
        word_id = []
        for w in words:
            if voc.contain(w):
                word_id.append(voc.get_word_index(w))
            else:
                word_id.append(-1)
        prob_all_cats = probability.Probability(1, class_num)
        for i in range(0, class_num):
            prob = 1
            for wid in word_id:
                if wid != -1:
                    if voc_prob.get_value(wid, i) == 0:
                        print('Error')
                    prob *= voc_prob.get_value(wid, i)
            prob_all_cats.set_value(0, i, prob)
        return prob_all_cats
