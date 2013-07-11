import sys
import datetime
sys.path.append('..')

from algorithm import sw


class _Plotter(object):
    def plot_callback(self):
        pass


class SWConfig(object):
    """One shall inherit this class to give more specific configurations."""
    def __init__(self, graph_size, edges):
        self.graph_size = graph_size
        self.edges = edges

    def edge_prob_func(self):
        return 0.5

    def target_eval_func(self):
        return 1

    def monitor_statistics(self):
        return 0.5


class TopicModel(object):
    def __init__(self):
        self.corpus = None
        self.topic_tree = None
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
        # This shall base on the likelihood and depth prior.
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
        if current_clustering == [] or level_counter == 1:
            # Generate initial configuration
            config = SWConfig(graph_size=5, edges=[(1, 2), (0, 3)])

        elif level_counter == 2:
            config = SWConfig(graph_size=5, edges=[(1, 2), (0, 3)])

        elif level_counter == 3:
            config = SWConfig(graph_size=5, edges=[(1, 2), (0, 3)])

        return config

    def __need_reform(self):
        """Returns if the current topic_tree needs reforming."""
        if (self.monitor.last_reform_date - datetime.datetime.now()) > datetime.timedelta(days=30):
            return True
        return False

    def __add_level_to_tree(self, current_clustering):
        """Add a level to tree."""


class ModelMonitor():
    def __init__(self):
        self.last_reform_date = datetime.datetime.now() - datetime.timedelta(year=1)
        self.reform_counter = 0

    def update_reform_time(self):
        self.last_reform_date = datetime.datetime.now()
        self.reform_counter += 1
