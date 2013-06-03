# Pursuit a topic tree.
import logging
import glob
import math
import copy

import numpy as np

from cooccurrence.cooccur_mat import CooccurMatrix
from storyclustering import storyclustering
from preprocessing import cleansing
from vocabulary import vocabulary

class TopicTree(object):
    def __init__(self, num_topics, distributions, vocabulary):
        super(TopicTree, self).__init__()
        self.nodes = range(0, num_topics)
        self.termial_distributions = distributions
        self.branch_distributions = distributions
        self.branch_terminals = [[x] for x in self.nodes]
        self.vocabulary = vocabulary

    def combine_branch(self, i, j):
        # combine node
        self.nodes[i] = [self.nodes[i]]
        self.nodes[i].append(self.nodes[j])
        self.nodes.pop(j)

        # transfer the terminals' ownership
        self.branch_terminals[i].extend(self.branch_terminals[j])
        self.branch_terminals.pop(j)

        # combine branch distribution
        self.branch_distributions[i] = self.branch_distributions[i] + self.branch_distributions[j]
        if self.branch_distributions[i].sum() != 0:
            self.branch_distributions[i] /= self.branch_distributions[i].sum()
        self.branch_distributions.pop(j)

    def find_branch_id(self, target):
        for (branch_id, terminals) in enumerate(self.branch_terminals):
            if target in terminals:
                return branch_id
        raise ValueError('Cannot find target terminal node: {0}'.format(target))

    def print_hiearchy(self, root=None, labels=None, level_indents=0):
        if root is None:
            root = self.nodes
        print('{0}+'.format(level_indents*'    '))
        for node in root:
            if isinstance(node, type([])):
                # Have next level
                self.print_hiearchy(node, labels=labels, level_indents=level_indents+1)
            else:
                if labels is not None:
                    label_to_print = labels[node]
                else:
                    label_to_print = node
                print('{0}{1}'.format((level_indents+1)*'    ', label_to_print))

    def get_probability(self, branch_id, word):
        try:
            word_id = self.vocabulary.get_word_index(word)
            distribution = self.branch_distributions[branch_id]
            assert(distribution[0, word_id] != 0)
            return distribution[0, word_id]
        except ValueError:
            logging.warning('Cannot find word: {0}'.format(word))
            return 1


def calculate_prior(n):
    """Returns the prior of the tree based on complexity.
    Simple trees are favored."""
    return math.exp(-n) * 1e20


def calculate_likelihood(tree, corpus, subset=None):
    """Calculate the likelihood of the corpus given a topic tree."""
    likelihood = 1
    for (idx, wordlist) in enumerate(corpus):
        # Only computer the likelihood of affected portion of data
        if subset is None or idx in subset:
            # The likelihood is calculated on the main branch.
            target_branch_id = tree.find_branch_id(idx)

            prob_doc = 1
            for word in wordlist:
                prob_doc *= tree.get_probability(target_branch_id, word)

            likelihood *= prob_doc
    assert(likelihood != 1)
    #if (likelihood == 1 or likelihood == 0):
    #    logging.warning('Subset to compute {0}'.format(subset))
    #    logging.warning('Words in subset:')
    #    for s in subset:
    #        logging.warning('{0}'.format(corpus[s]))
    #    raise ValueError('Likelihood is 1 or 0.')
    return likelihood


def propose_next(current_tree):
    """Purpose new trees by pairwise combination."""
    num_main_branches = len(current_tree.nodes)
    canididates = []
    # Here we perform a exhaust search to propose all possible combinations.
    # Heuristics can be added to skip certain candidates.
    for x in range(0, num_main_branches):
        for y in range(0, num_main_branches):
            if (x < y):
                # Combine node x and y
                new_tree = copy.deepcopy(current_tree)
                new_tree.combine_branch(x, y)

                affected = copy.deepcopy(current_tree.branch_terminals[x])
                affected.extend(current_tree.branch_terminals[y])
                canididates.append((new_tree, affected))
    return canididates


def greedy_pursuit(initial_tree, corpus):
    best_candidate = initial_tree
    max_posterior_gain = 1

    while (max_posterior_gain > 0):
        current_tree = best_candidate
        current_prior = calculate_prior(len(current_tree.nodes))
        logging.debug('Tree: {0}'.format(current_tree.nodes))

        # Generate candidates
        logging.info('Generating candidates...')
        new_candidates = propose_next(current_tree)
        logging.debug('# of candidates: {0}'.format(len(new_candidates)))

        # Prior for all candidates are same, since
        candidate_prior = calculate_prior(len(current_tree.nodes)-1)

        logging.info('Evaluating candidates...')
        max_posterior_gain = -1
        for (candidate_tree, affected_terminals) in new_candidates:
            # Posterior for candidate: P(T2|D) = P(D|T2)P(T2)
            candidate_lh_affected = calculate_likelihood(candidate_tree, corpus, subset=affected_terminals)
            candidate_posterior = candidate_lh_affected * candidate_prior

            # Posterior for current: P(T1|D) = P(D|T1)P(P1)
            current_lh_affected = calculate_likelihood(current_tree, corpus, subset=affected_terminals)
            current_posterior = current_lh_affected * current_prior

            posterior_gain = candidate_posterior - current_posterior
            if (posterior_gain > max_posterior_gain):
                logging.debug('Likelihood Candidate v. Current: {0} vs. {1}'.format(
                    candidate_lh_affected, current_lh_affected))
                logging.debug('Gain: {0}'.format(posterior_gain))

                best_candidate = candidate_tree
                max_posterior_gain = posterior_gain
        logging.debug('Posterior Gain: {0}'.format(max_posterior_gain))

    return current_tree


def pursuit_tree(input_triplet_files, co_mat_file=None, diffuse=False):
    if co_mat_file is not None:
        np_cooccur = CooccurMatrix()
        np_cooccur.load(co_mat_file)
        vocab = np_cooccur.vocabulary
    else:
        # Build vocabulary
        logging.info('Building vocabulary...')
        vocab = build_vocabulary(input_triplet_files)

    # calculate histogram
    logging.info('Calculating histograms of each story...')
    corpus = []
    distributions = []
    for triplet_file in input_triplet_files:
        (hist, wordlist) = storyclustering.learn_story_histogram(triplet_file, vocab)
        if co_mat_file is not None and diffuse is True:
            hist = np.dot(hist, np_cooccur.matrix)
        #hist = np.array([0.2, 0.6, 0.2])
        #wordlist = ['a', 'b', 'c']
        corpus.append(wordlist)
        distributions.append(hist)

    # initial tree
    logging.info('Calculating Initial Tree...')
    initial_tree = TopicTree(len(input_triplet_files), distributions, vocab)
    #initial_tree = TopicTree(len(input_triplet_files), distributions, ['a', 'b', 'c'])
    #return initial_tree

    # start pursuit
    logging.info('Pursuing a optimum tree...')
    optimum_tree = greedy_pursuit(initial_tree, corpus)
    return optimum_tree


def build_vocabulary(input_triplet_files, word_type='NP1'):
    vocab = vocabulary.Vocabulary()
    for triplet_file in input_triplet_files:
        with open(triplet_file, 'r') as f:
            for line in f:
                if(line[0] != '<'):
                    line = (line[:-2]).lower()
                    triplets = line.split('|')
                    if (word_type == 'NP1'):
                        words = cleansing.clean(triplets[0].split())
                    elif (word_type == 'VP'):
                        words = cleansing.clean(triplets[1].split())
                    elif (word_type == 'NP2'):
                        words = cleansing.clean(triplets[2].split())
                    for w in words:
                        vocab.add(w)
    logging.info('Vocabulary built. # of words: {0}'.format(vocab.size()))
    return vocab


def main():
    logging.basicConfig(level=logging.DEBUG)

    # input data
    input_triplet_files = glob.glob('triplet_files_small/*.txt')
    input_triplet_files.sort()
    logging.debug('Files {0}'.format(len(input_triplet_files)))

    # pursuit tree on NP1
    optimum_tree = pursuit_tree(input_triplet_files)  # 'mat/np1_co_mat')

    # ---For test---
    #optimum_tree.combine_branch(1, 10)
    #optimum_tree.combine_branch(1, 5)
    # ---End---

    labels = [filename.split('/')[-1][:-4] for filename in input_triplet_files]
    optimum_tree.print_hiearchy(labels=labels)
    return


if __name__ == '__main__':
    main()
