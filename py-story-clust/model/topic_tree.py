import logging
import math
import copy
import numpy as np

from model import *
from model.corpus import BranchStatistics


class TopicTree(object):
    def __init__(self, corpus_stat):
        super(TopicTree, self).__init__()
        self.nodes = range(0, corpus_stat.size())
        self.corpus_stat = corpus_stat
        self.branch_stats = [BranchStatistics(doc_stat) for doc_stat in copy.deepcopy(corpus_stat.documents_stats)]
        self.branch_terminals = [[x] for x in self.nodes]
        self.inter_distance = self.__calculate_inter_distance()

    def combine_branch(self, i, j):
        # Combine node.
        self.nodes[i] = [self.nodes[i]]
        self.nodes[i].append(self.nodes[j])
        self.nodes.pop(j)

        # Transfer the terminals' ownership.
        self.branch_terminals[i].extend(self.branch_terminals[j])
        self.branch_terminals.pop(j)

        # Combine branch distribution.
        self.branch_stats[i].combine(self.branch_stats[j])
        self.branch_stats.pop(j)
        # Recalculate intra branch distance.
        self.branch_stats[i].calcualte_intra_distance(self.corpus_stat, self.branch_terminals[i])

        # Update the inter branch distance matrix.
        # TODO: Here the whole matrix is re-calculated. Actually we can only
        #       calculate the affected part to improve efficiency.
        self.inter_distance = self.__calculate_inter_distance()

    def synthesize_title(self, branch_id):
        all_word_ids = self.branch_stats[branch_id].synthesize_title()
        #return '{0}'.format(all_word_ids)

        sub_titles = []
        for (type_id, word_ids) in enumerate(all_word_ids):
            words = [self.corpus_stat.vocabularies[type_id].get_word(wid) for wid in word_ids]
            sub_titles.append(' '.join(words))
        return 'Tag: ' + ' | '.join(sub_titles)

    def dunn_index(self):
        """Calculate Dunn Index of the cluster.
        A higher Dunn index indicates better clustering: dense and well-separated."""
        max_intra_distance = 0
        for branch in self.branch_stats:
            if branch.intra_distance > max_intra_distance:
                max_intra_distance = branch.intra_distance

        min_distance = float("inf")
        for i in range(0, len(self.branch_stats)):
            for j in range(0, len(self.branch_stats)):
                if i >= j:
                    continue
                distance = self.inter_distance[i, j]/max_intra_distance

                # Update min distance.
                if distance < min_distance:
                    min_distance = distance
        return min_distance

    def prior(self):
        """Returns the prior of the tree based on complexity.
        Simple trees are favored."""
        return math.exp(-len(self.branch_stats) * 10)  # * 1e30

    def likelihood(self, corpus, subset=None, weights=[1, 1, 1]):
        """Calculate the likelihood of the corpus of current topic tree."""
        likelihood = 0
        for (doc_id, document) in enumerate(corpus.documents):
            # Only computer the likelihood of affected portion of data
            if subset is None or doc_id in subset:
                # The likelihood is calculated on the main branch.
                target_branch_id = self.__find_branch_id(doc_id)

                prob_doc = 0
                for type_id in range(0, NUM_WORD_TYPE):
                    if (len(document.word_lists[type_id]) == 0):
                        continue
                        #raise ValueError('Empty list in document {0}, list {1}'.format(
                        #    document.name, type_id))
                    prob_type = 0
                    for word in document.word_lists[type_id]:
                        # calculate log likelihood
                        prob_type += math.log(self.__get_probability(target_branch_id, word, type_id))
                    #prob_type /= len(document.word_lists[type_id])
                    prob_doc += prob_type * weights[type_id] / sum(weights)

                likelihood += prob_doc
        #assert(likelihood != 0)
        return likelihood

    def __find_branch_id(self, target_terminal):
        for (branch_id, terminals) in enumerate(self.branch_terminals):
            if target_terminal in terminals:
                return branch_id
        raise ValueError('Cannot find target terminal node: {0}'.format(target_terminal))

    def __get_probability(self, branch_id, word, type_id):
        try:
            word_id = self.corpus_stat.vocabularies[type_id].get_word_index(word)
            distribution = self.branch_stats[branch_id].distributions[type_id]
            assert(distribution[word_id] > 0)
            return distribution[word_id]
        except ValueError:
            logging.warning('Cannot find word: {0}   (type {1})'.format(word, type_id))
            return 1

    def print_hiearchy(self, labels=None, synthesize_title=False):
        self.__print_hiearchy_recursive(root=self.nodes, labels=labels, synthesize_title=synthesize_title)

    def __print_hiearchy_recursive(self, root=None, labels=None, level_indents=0, synthesize_title=False, branch_id=0):
        if root is None:
            root = self.nodes

        if synthesize_title and level_indents == 1:
            print('{0}+ {1}'.format('|  ', self.synthesize_title(branch_id)))
        else:
            print('{0}+'.format(level_indents*'|  '))
        for (bid, node) in enumerate(root):
            if isinstance(node, type([])):
                # Have next level
                self.__print_hiearchy_recursive(
                    node, labels=labels, level_indents=level_indents+1, synthesize_title=synthesize_title, branch_id=bid)
            else:
                if labels is not None:
                    label_to_print = labels[node]
                else:
                    label_to_print = node
                print('{0}{1}{2}'.format((level_indents)*'|  ', '|- ', label_to_print))

    def print_hiearchy_json(self, fw, labels=None, synthesize_title=False):
        self.__print_hiearchy_recursive_json(fw, root=self.nodes, labels=labels, synthesize_title=synthesize_title)

    def __print_hiearchy_recursive_json(self, fw, root=None, labels=None, level_indents=0, synthesize_title=False, branch_id=0):
        if root is None:
            root = self.nodes

        fw.write(level_indents*'  '+'{')
        if synthesize_title and level_indents == 1:
            fw.write((level_indents+1)*'  ' + '"name": "{0}",'.format(self.synthesize_title(branch_id)))
            #print('{0}+ {1}'.format('|  ', self.synthesize_title(branch_id)))
        else:
            fw.write((level_indents+1)*'  ' + '"name": "{0}",'.format(branch_id))
            #print('{0}+'.format(level_indents*'|  '))
        if len(root) > 0:
            fw.write((level_indents+1)*'  ' + '"children": [')
            for (bid, node) in enumerate(root):
                if isinstance(node, type([])):
                    # Have next level
                    self.__print_hiearchy_recursive_json(
                        fw, node, labels=labels, level_indents=level_indents+1, synthesize_title=synthesize_title, branch_id=bid)
                    if node != root[-1]:
                        fw.write((level_indents+1)*'  ' + ',')
                else:
                    if labels is not None:
                        label_to_print = labels[node]
                    else:
                        label_to_print = node

                    append = ''
                    if node != root[-1]:
                        append = ','
                    fw.write((level_indents+1)*'  ' + '{' + '"name": "{0}"'.format((label_to_print)) + '}' + append)
            fw.write((level_indents+1)*'  ' + ']')
        fw.write(level_indents*'  '+'}')

    def __calculate_inter_distance(self):
        """Calculate the inter branch distance matrix D.
        Each element D(i, j) is the TV norm between branch distributions of i and j."""
        distances_mat = np.zeros([len(self.branch_stats), len(self.branch_stats)])
        for (branch_i, branch_stat_i) in enumerate(self.branch_stats):
            for (branch_j, branch_stat_j) in enumerate(self.branch_stats):
                if branch_i >= branch_j:
                    # Only calculate half of the matrix since the distance is symmetric.
                    continue

                # Calculate distance by TV norm.
                d = 0
                word_types_to_use = [WORD_TYPE_NP1, WORD_TYPE_VP, WORD_TYPE_NP2]
                for type_id in word_types_to_use:
                    distr_i = branch_stat_i.distributions[type_id].hist
                    distr_j = branch_stat_j.distributions[type_id].hist
                    tv_norm = calculate_tv_norm(distr_i, distr_j)
                    d += tv_norm

                # Average among word types.
                d /= len(word_types_to_use)
                distances_mat[branch_i, branch_j] = d
        return distances_mat

    def calculate_distribution_distance(self):
        dif_min = 10
        for (stats_id1, stats1) in enumerate(self.branch_stats):
            for (stats_id2, stats2) in enumerate(self.branch_stats):
                if stats_id1 >= stats_id2:
                    continue
                dif = 0
                for type_id in [0, 2]:
                    distribution1 = self.branch_stats[branch_i].distributions[type_id].hist
                    distribution2 = self.branch_stats[branch_j].distributions[type_id].hist
                    dif += self.__calculate_tv_norm(distribution1, distribution2)
                dif /= 2
                if dif_min > dif:
                    dif_min = dif
                    id1 = stats_id1
                    id2 = stats_id2
        return [dif_min, id1, id2]
