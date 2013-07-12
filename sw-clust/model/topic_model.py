import sys
import datetime
sys.path.append('..')

import numpy as np
import mpmath
from scipy.stats import norm

from preprocessing import vacabulary
from algorithm import sw


class _Plotter(object):
    def __init__(self):
        pass

    def plot_callback(self, clustering, context):
        # TODO: some drawings.
        pass


class SWConfig(object):
    """One shall inherit this class to give more specific configurations."""
    def __init__(self, graph_size, edges, vertex_distribution, documents, level):
        self.graph_size = graph_size
        self.edges = edges
        self.monitor_statistics = self.energy
        self.vertex_distribution
        self.level = level
        self.documents = documents

    def edge_prob_func(self, s, t, context):
        """Calculate edge probability based on KL divergence."""
        p = self.vertex_distribution[s]
        q = self.vertex_distribution[t]
        assert(len(p) == len(q))
        kl_array_pq = [p[i]*(mpmath.log(p[i] + 1e-100) - mpmath.log(q[i]) + 1e-100) for i in range(0, len(p))]
        kl_pq = mpmath.sum(kl_array_pq)
        kl_array_qp = [q[i]*(mpmath.log(q[i] + 1e-100) - mpmath.log(p[i]) + 1e-100) for i in range(0, len(p))]
        kl_qp = mpmath.sum(kl_array_qp)
        # TO BE DISCUSSED: Using the same or different temperature settings?
        temperature = self.cooling_schedule(context.iteration_counter)
        return mpmath.exp(-(kl_pq + kl_qp)*temperature/2)

    def target_eval_func(self, clustering, context=None):
        temperature = self.cooling_schedule(context.iteration_counter)
        return mpmath.exp(- self.energy(clustering) / temperature)

    def energy(self, clustering):  # Need the distribution here. How to add it?
        energy = 0.0
        # TODO: target function may depend on level.
        # Candidate terms: likelihood, time prior, and etc.
        #     energy += -mpmath.log(P)
        for cluster in clustering:
            energy += -mpmath.log(self.__likelihood(cluster)) - mpmath.log(self.__time_prior(cluster))
        return energy

    def __likelihood(self, cluster, weights=[1]*NUM_WORD_TYPE):
        likelihood = 0.0
        # TODO: Calculate the likelihood
        for node_index in cluster:
            for type_id in range(0, NUM_WORD_TYPE):
                if (len(document.word_lists[type_id]) == 0):
                    continue
                prob_type = 0
                for word in document.word_lists[type_id]:
                    prob_type += math.log(self.__get_probability(target_branch_id, word, type_id))
                prob_doc += prob_type * weights[type_id] / sum(weights)
            likelihood += 0
        return likelihood

    def __time_prior(self, cluster):
        time_series = []
        for node_index in cluster:
            time_series.append()  # TODO: Get the corresponding time of the story
        time_series.sort()
        dif = 0.0
        for i in range(0, len(time_series)-1):
            date_dif = time_series(i+1) - time_series(i)
            dif += date_dif.days
        dif /= (len(time_series) - 1)
        return mpmath.mpf(norm(1, 5).pdf(dif))

    def cooling_schedule(self, iteration_counter):
        # TODO: Cooling schedule may depend on level.
        starting_temperature = 1000
        period = 2
        step_size = 10

        temperature = starting_temperature - int(iteration_counter/period)*step_size
        if temperature <= 0:
            temperature = 0.1
        return temperature


class TopicModel(object):
    def __init__(self):
        self.corpus = None  # No further use?
        self.topic_tree = _Tree()
        self.date_range = None
        self.monitor = ModelMonitor()
        pass

    def feed(self, new_corpus):
        # Do Segmentation (if not segmented)
        if not new_corpus.segmented:
            # TODO: Do segmentation first
            pass

        # Inference and attach to trees
        for document in new_corpus.documents:
            self.__inference(document)
            self.corpus.add_document(document)

        # Reform the tree if necessary.
        if (self.__need_reform()):
            self.__reform_by_multilevel_sw()
        pass

    def __inference(self, new_document):
        """Inference and attach the new document to the current topic tree."""
        # TODO: This shall base on the likelihood and depth prior.
        pass

    def __reform_by_multilevel_sw(self):
        """Reform the whole tree by doing multi-level SW-Cuts."""

        plotter = _Plotter()
        current_clustering = []
        need_next_level = True
        level_counter = 0

        while need_next_level:
            level_counter += 1
            config = self.__generate_sw_configuration(current_clustering, level_counter)

            # Clustering by SW.
            current_clustering = sw.sample(
                config.graph_size,
                config.edges,
                config.edge_prob_func,
                config.target_eval_func,
                intermediate_callback=plotter.plot_callback,
                initial_clustering=None,
                monitor_statistics=config.monitor_statistics)

            # Save current clustering as a new level to the tree.
            self.__add_level_to_tree(current_clustering)

            # Determine if need more level.
            # TODO: determine if need next level.
            need_next_level = True
        pass

    def __generate_sw_configuration(self, current_clustering, level_counter):
        """Generate sw configuration for next run base on current clustering result."""
        # TODO: give different configurations based on level.
        #if current_clustering == [] or level_counter == 1:
        #    # Generate initial configuration
        #    config = SWConfig(graph_size=15, edges=[(1, 2), (0, 3)], level=level_counter)

        #elif level_counter == 2:
        #    config = SWConfig(graph_size=10, edges=[(1, 2), (0, 3)], level=level_counter)

        #elif level_counter == 3:
        #    config = SWConfig(graph_size=5, edges=[(1, 2), (0, 3)], level=level_counter)

        graph_size = len(current_clustering)
        # Generate the edges. Delete some edges in the complete graph using some criteria.
        edges = []
        distance_threshold = 0.5*level_counter  # TODO: Decide the threshold based on the current level
        for i in range(0, graph_size-1):
            for j in range(i+1, graph_size):
                dist_i = []  # TODO: Add the distribution
                dist_j = []
                distance = calculate_tv_norm(dist_i, dist_j)
                if distance <= distance_threshold:
                    edges.append((i, j))
                    edges.append((j, i))
        config = SWConfig(graph_size, edges, vertex_distribution=None, corpus=self.corpus.documents, level=level_counter)
        return config

    def __need_reform(self):
        """Returns if the current topic_tree needs reforming."""
        if (self.monitor.last_reform_date - datetime.datetime.now()) > datetime.timedelta(days=30):
            return True
        # TODO: Add other criterion for judging whether reforming the tree
        #       is needed, like Dunn Index, Davies-Bouldin Index, etc.
        return False

    def __add_level_to_tree(self, current_clustering):
        """Add a level to tree."""
        self.topic_tree.add_level_on_top(current_clustering)
        pass


class ModelMonitor():
    def __init__(self):
        self.last_reform_date = datetime.datetime.now() - datetime.timedelta(year=1)
        self.reform_counter = 0

    def update_reform_time(self):
        self.last_reform_date = datetime.datetime.now()
        self.reform_counter += 1


class _Distribution(object):
    """A 1D histogram (normalized to 1)."""
    def __init__(self, hist, denominator):
        self.hist = hist
        self.denominator = denominator

    def combine(self, other):
        # Recover the histogram before normalization and add up two histograms
        self.hist = self.hist * self.denominator + other.hist * other.denominator

        # Re-normalize to 1
        denominator = self.hist.sum()
        if denominator != 0:
            self.hist /= denominator
        self.denominator = denominator

    def synthesize(self, num_words):
        """Synthesize a set of words from the distribution."""
        indexes = np.argsort(self.hist)
        top_words_id = indexes[0][::-1][0:min(num_words, np.shape(self.hist)[1])]
        return top_words_id.tolist()

    def __getitem__(self, word_id):
        return self.hist[0, word_id]


#
# Definitions for Topic Tree.
#
class _TreeNode(object):
    def __init__(self):
        self.__children = []
        self.__vp_distribution = None
        self.__np1_distribution = None
        self.__np2_distribution = None
        self.__time = 0

    def add_child(self, node):
        self.__children.append(node)
        # TODO: merge distribution after add a child
        # What if add a node to a terminal node (document).

    def get_child(self, index):
        return self.__children[index]

    def is_terminal(self):
        return (len(self.__children) == 0)

    def get_time(self):
        return self._time


class _Tree(object):
    """A Tree structure."""
    def __init__(self):
        self.__root = _TreeNode()

    def add_to_root(self, node):
        """Add a node to the root."""
        self.__root.add_child(node)

    def add_level_on_top(self, clustering):
        """Add a new level on the top of the tree."""
        # e.g. clustering = [{1,2,3}, {4,5}, {5,6,7}]
        new_root = _TreeNode()
        for cluster in clustering:
            new_parent_node = _TreeNode()
            for vertex_index in cluster:
                new_parent_node.add_child(self.__root.get_child(vertex_index))
        self.__root = new_root


#
# Definitions for corpus and document.
#
class _Corpus(object):
    """A Corpus object includes all documents' feature and corpus vocabulary."""
    def __init__(self):
        self.documents = []
        np1_vocab = vocabulary.Vocabulary()
        vp_vocab = vocabulary.Vocabulary()
        np2_vocab = vocabulary.Vocabulary()
        self.vocabularies = (np1_vocab, vp_vocab, np2_vocab)

    def add_document(self, document):
        # convert document to document feature.
        # probably need to adjust vocabulary. (change other documents' feature vector)

        # generate document histogram

        # save document
        document_feature = _DocumentFeature()
        self.documents.append(document_feature)

    def get_document_name(self, doc_id):
        return self.documents[doc_id].name

    def size(self):
        return len(self.documents)

    def vocabulary_size(self, word_type):
        assert(word_type < NUM_WORD_TYPE)
        return len(self.vocabularies[word_type])


class _DocumentFeature(object):
    def __init__(
            self,
            name,
            timestamp,
            np1_vector,
            vp_vector,
            np2_vector,
            np1_distribution,
            vp_distribution,
            np2_distribution,
            ocr_words):
        self.name = name
        self.timestamp = timestamp
        self.word_vectors = (np1_vector, vp_vector, np2_vector)
        self.ocr_words = ocr_words

        # FIXME: Probably don't need to store distribution.
        self.distributions = (np1_distribution, vp_distribution, np2_distribution)
