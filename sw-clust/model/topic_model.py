import sys
import datetime
sys.path.append('..')

from algorithm import sw


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
            self.__reform_by_sw()
        pass

    def __inference(self, new_document):
        """Inference and attach the new document to the current topic tree."""
        pass

    def __reform_by_sw(self):
        """Reform the whole tree by doing multi-level SW-Cuts."""
        current_level = 0
        max_labels_agenda = [10, 5]
        while current_level < len(max_labels_agenda):
            num_labels_this_level = max_labels_agenda[current_level]

            samples = sw.sample(
                _AdjacencyGraph(graph_size, edges),
                self.edge_prob_func,
                self.target_eval_func,
                intermediate_callback=None,
                initial_labeling=None,
                max_labels=num_labels_this_level)

            # pick one sample from samples
            sample = samples[0]

            # reform the graph setting for next level.
            graph_size = 0
            edges = []

            current_level += 1
        pass

    def __need_reform(self):
        """Returns if the current topic_tree needs reforming."""
        if (self.monitor.last_reform_date - datetime.datetime.now()) > datetime.timedelta(days=30):
            return True
        return False

    def edge_prob(self, s, t, context):
        # The connectivity depends on multiple criterion
        #  - time
        #  - likelihood
        return 0.5

    def target_prob(self, labeling):
        # Evaluate the target probability (up to a constant).
        return self.topic_tree.prior() * self.topic_tree.likelihood(self.corpus)


class ModelMonitor():
    def __init__(self):
        self.last_reform_date = datetime.datetime.now() - datetime.timedelta(year=1)
        self.reform_counter = 0

    def update_reform_time(self):
        self.last_reform_date = datetime.datetime.now()
        self.reform_counter += 1
