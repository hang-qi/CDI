import sys
import datetime
sys.path.append('..')

import numpy as np
import mpmath

from algorithm import sw


class _Plotter(object):
    def __init__(self):
        pass

    def plot_callback(self, clustering, context):
        # TODO: some drawings.
        pass


class SWConfig(object):
    """One shall inherit this class to give more specific configurations."""
    def __init__(self, graph_size, edges, level):
        self.graph_size = graph_size
        self.edges = edges
        self.level = level
        self.monitor_statistics = self.energy

    def edge_prob_func(self, s, t, context):
        # TODO: calculate base on KL divergence.
        return 0.5

    def target_eval_func(self, clustering, context=None):
        temperature = self.cooling_schedule(context.iteration_counter)
        return mpmath.exp(- self.energy() / temperature)

    def energy(self, clustering):
        energy = 0
        # TODO: target function may depend on level.
        # Candidate terms: likelihood, time prior, and etc.
        #     energy += -mpmath.log(P)
        return energy

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
            self.__inference(document)

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
        if current_clustering == [] or level_counter == 1:
            # Generate initial configuration
            config = SWConfig(graph_size=15, edges=[(1, 2), (0, 3)], level=level_counter)

        elif level_counter == 2:
            config = SWConfig(graph_size=10, edges=[(1, 2), (0, 3)], level=level_counter)

        elif level_counter == 3:
            config = SWConfig(graph_size=5, edges=[(1, 2), (0, 3)], level=level_counter)

        return config

    def __need_reform(self):
        """Returns if the current topic_tree needs reforming."""
        if (self.monitor.last_reform_date - datetime.datetime.now()) > datetime.timedelta(days=30):
            return True
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


class _TreeNode(object):
    def __init__(self):
        self.__children = []
        self.__vp_distribution = None
        self.__np1_distribution = None
        self.__np2_distribution = None

    def add_child(self, node):
        self.__childend.append(node)
        # TODO: merge distribution after add a child
        # What if add a node to a terminal node (document).

    def get_child(self, index):
        return self.__children[index]

    def is_terminal(self):
        return (len(self.__children) == 0)


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
