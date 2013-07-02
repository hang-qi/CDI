

class AdjacencyGraph(object):
    """Adjacency Graph on which to perform Swendsen-Wang Cuts."""
    def __init__(self, arg):
        super(AdjacencyGraph, self).__init__()
        return


class SWCuts(object):
    """Swendsen-Wang cuts."""
    def __init__(self):
        super(SWCuts, self).__init__()

    def run(self, adjacency_graph, edge_prob_func, target_evaluation_func):
        self.current_state = adjacency_graph
        while not self.__has_converged():
            connected_components = self.__form_connected_components(edge_prob_func)
            self.current_state = self.__flip_connected_components(
                connected_components, target_evaluation_func)
        return

    def __has_converged(self):
        pass

    def __form_connected_components(self, edge_prob_func):
        pass

    def __flip_connected_components(self, target_evaluation_func):
        newstate = self.current_state
        return newstate

return
