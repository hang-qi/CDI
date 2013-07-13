import sys
import datetime
sys.path.append('..')

import numpy as np
import mpmath
from scipy.stats import norm

from model import *
from preprocessing import vocabulary
from algorithm import sw


class _Plotter(object):
    def __init__(self):
        pass

    def plot_callback(self, clustering, context):
        # TODO: some drawings.
        pass


class SWConfig(object):
    """One shall inherit this class to give more specific configurations."""
    def __init__(self, graph_size, edges, vertex_distributions, documents, level):
        self.graph_size = graph_size
        self.edges = edges
        self.monitor_statistics = self.energy
        self.vertex_distributions = vertex_distributions
        self.level = level
        self.documents = documents

    def edge_prob_func(self, s, t, context):
        """Calculate edge probability based on KL divergence."""
        p = self.vertex_distributions[s]
        q = self.vertex_distributions[t]
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
        return mpmath.exp(- self.energy(clustering, context.iteration_counter) / temperature)

    def energy(self, clustering, iteration_counter):  # Need the distribution here. How to add it?
        energy = 0.0
        # TODO: target function may depend on level.
        # Candidate terms: likelihood, time prior, and etc.
        #     energy += -mpmath.log(P)
        for cluster in clustering:
            energy += -mpmath.log(self.__likelihood(cluster))
        if iteration_counter == 1:
            for cluster in clustering:
                energy += -mpmath.log(self.__time_prior(cluster))
        return energy

    def _likelihood(self, cluster, weights=[1]*NUM_WORD_TYPE):
        likelihood = 0.0
        # First generate the distribution of the current cluster
        cluster_distribution = mpmath.matrix(1, len(self.vertex_distributions[0]))
        for dist_index in cluster:
            cluster_distribution += self.vertex_distributions(dist_index)
        return likelihood

    def _time_prior(self, cluster):
        time_series = []
        for doc_id in cluster:
            time_series.append(self.documents[doc_id].timestamp)
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
        self.corpus = None
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
            self._inference(document)
            self.corpus.add_document(document)

        # Reform the tree if necessary.
        if (self._need_reform()):
            self._reform_by_multilevel_sw()
        pass

    def _inference(self, new_document):
        """Inference and attach the new document to the current topic tree."""
        # TODO: This shall base on the likelihood and depth prior.
        pass

    def _reform_by_multilevel_sw(self):
        """Reform the whole tree by doing multi-level SW-Cuts."""

        plotter = _Plotter()
        need_next_level = True
        level_counter = 0

        current_vertex_distributions = self._calculate_initial_vertex_distributions()
        current_clustering = [set([v]) for v in range(0, len(self.corpus))]

        while need_next_level:
            level_counter += 1
            config = self._generate_next_sw_config(
                current_vertex_distributions, current_clustering, level_counter)

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
            self._add_level_to_tree(current_clustering)

            # Determine if need more level.
            # TODO: determine if need next level.
            need_next_level = True
        pass

    def _calculate_initial_vertex_distributions(self):
        initial_vertex_distributions = []
        for document in self.corpus:
            vertex_distribution = _VertexDistribution()
            for word_type in WORD_TYPES:
                vertex_distribution[word_type] = self.corpus.doc_to_distribution(document, word_type)
            initial_vertex_distributions.append(vertex_distribution)
        return initial_vertex_distributions

    def _combine_vertex_distributions_given_clustering(self, current_vertex_distributions, clustering):
        # create new vertex distribution
        new_vertex_distributions = []
        for cluster in clustering:
            vertex_distribution = _VertexDistribution()
            for v in cluster:
                vertex_distribution += current_vertex_distributions[v]
            new_vertex_distributions.append(vertex_distribution)
        return new_vertex_distributions

    def _generate_next_sw_config(self, current_vertex_distributions, current_clustering, level_counter):
        """Generate sw configuration for next run base on current clustering result."""
        # TODO: give different configurations based on level.
        graph_size = len(current_clustering)

        # create new vertex distribution
        next_vertex_distributions = _combine_vertex_distributions_given_clustering(
            current_vertex_distributions, current_clustering)

        # Generate the edges. Delete some edges in the complete graph using some criteria.
        edges = []
        # TODO: Decide the threshold based on the current level
        distance_threshold = 0.5*level_counter
        for i in range(0, graph_size-1):
            for j in range(i+1, graph_size):
                dist_i = vertex_distribution[i]
                dist_j = vertex_distribution[j]
                distance = calculate_tv_norm(dist_i, dist_j)
                if distance <= distance_threshold:
                    edges.append((i, j))
                    edges.append((j, i))

        config = SWConfig(graph_size, edges, vertex_distributions=next_vertex_distributions, corpus=self.corpus.documents, level=level_counter)
        return config

    def _need_reform(self):
        """Returns if the current topic_tree needs reforming."""
        if (self.monitor.last_reform_date - datetime.datetime.now()) > datetime.timedelta(days=30):
            return True
        # TODO: Add other criterion for judging whether reforming the tree
        #       is needed, like Dunn Index, Davies-Bouldin Index, etc.
        return False

    def _add_level_to_tree(self, current_clustering):
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


#
# Definitions for Topic Tree.
#
class _TreeNode(object):
    def __init__(self):
        self._children = []
        self._vp_distribution = None
        self._np1_distribution = None
        self._np2_distribution = None

    def add_child(self, node):
        self._children.append(node)
        # TODO: merge distribution after add a child
        # What if add a node to a terminal node (document).

    def get_child(self, index):
        return self._children[index]

    def is_terminal(self):
        return (len(self._children) == 0)


class _Tree(object):
    """A Tree structure."""
    def __init__(self):
        self._root = _TreeNode()

    def add_to_root(self, node):
        """Add a node to the root."""
        self._root.add_child(node)

    def add_level_on_top(self, clustering):
        """Add a new level on the top of the tree."""
        # e.g. clustering = [{1,2,3}, {4,5}, {5,6,7}]
        new_root = _TreeNode()
        for cluster in clustering:
            new_parent_node = _TreeNode()
            for vertex_index in cluster:
                new_parent_node.add_child(self._root.get_child(vertex_index))
        self._root = new_root


#
# Definitions for corpus and document.
#
class Corpus(object):
    """A Corpus object includes all documents' feature and corpus vocabulary."""
    def __init__(self):
        self.documents = []
        np1_vocab = vocabulary.Vocabulary()
        vp_vocab = vocabulary.Vocabulary()
        np2_vocab = vocabulary.Vocabulary()
        self.vocabularies = (np1_vocab, vp_vocab, np2_vocab)

    def __len__(self):
        return len(self.documents)

    def __iter__(self):
        return iter(self.documents)

    def __getitem__(self, document_id):
        return self.documents[document_id]

    def add_document(self, original_doc):
        """Convert document to feature and save into document list."""
        document_feature = self._convert_doc_to_feature(original_doc)
        self.documents.append(document_feature)

    def _convert_doc_to_feature(self, original_doc):
        document_feature = _DocumentFeature(original_doc.filename, original_doc.timestamp)
        document_feature.ocr_words = original_doc.ocr_words

        for word_type in WORD_TYPES:
            document_feature.word_ids[word_type] = self._convert_words_to_ids(word_type, original_doc.word_lists[word_type])
        return document_feature

    def _convert_words_to_ids(self, word_type, word_list):
        assert(word_type < NUM_WORD_TYPE)
        ids = []
        for word in word_list:
            # If word is in current vocabulary, we directly look up the word_id.
            # Otherwise, we add this word to the vocabulary and then look up.
            if word not in self.vocabularies[word_type]:
                self.vocabularies[word_type].add(word_type)
            word_id = self.vocabularies[word_type].get_word_index(word)
            ids.append(word_id)
        return ids

    def get_document_name(self, doc_id):
        return self.documents[doc_id].name

    def vocabulary_size(self, word_type):
        assert(word_type < NUM_WORD_TYPE)
        return len(self.vocabularies[word_type])


class _DocumentFeature(object):
    def __init__(
            self,
            name,
            timestamp,
            np1_word_ids=None,
            vp_word_ids=None,
            np2_word_ids=None,
            ocr_words=None):
        self.name = name
        self.timestamp = timestamp
        self.word_ids = [np1_word_ids, vp_word_ids, np2_word_ids]
        self.ocr_words = ocr_words


class _VertexDistribution:
    # Three _Distribution objects
    def __init__(self):
        self.distributions = [None] * NUM_WORD_TYPE

    def __getitem__(self, word_type):
        assert(word_type < NUM_WORD_TYPE)
        return self.distributions[word_type]

    def __setitem__(self, word_type, distribution):
        assert(word_type < NUM_WORD_TYPE)
        self.distributions[word_type] = distribution

    def __add__(self, other):
        result = _VertexDistribution()
        for word_type in WORD_TYPES:
            if self.distributions[word_type] is None:
                result.distributions[word_type] = other.distributions[word_type]
            else:
                result.distributions[word_type] = self.distributions[word_type] + other.distributions[word_type]
        return result

    def __radd__(self, other):
        return self.__add__(other)

    def __iadd__(self, other):
        return self.__add__(other)


class _Distribution(object):
    """A 1D histogram (normalized to 1)."""
    def __init__(self, length):
        self._hist = np.zeros(length)
        self._denominator = 0
        self._length = length

    def set_histogram(self, histogram):
        self._hist = histogram
        self._denominator = sum(histogram)
        if self._denominator != 1 and self._denominator != 0:
            self._hist /= self._denominator

    def __getitem__(self, word_id):
        return self._hist[word_id]

    def __add__(self, other):
        # Recover histogram and add.
        result = _Distribution(self._length)
        new_hist = self._hist * self._denominator + other._hist * other._denominator
        result.set_histogram(new_hist)
        return result

    def __radd__(self, other):
        # The 'add' operation among distribution if symmetric.
        return self.__add__(other)

    def __iadd__(self, other):
        return self.__add__(other)

    def kl_divergence(self, other):
        return kl_value

    def combine(self, other):
        self = self.__add__(other)

    def synthesize(self, num_words):
        """Synthesize a set of words from the distribution."""
        indexes = np.argsort(self._hist)
        top_words_id = indexes[::-1][0:min(num_words, len(self._hist))]
        return top_words_id.tolist()
