from collections import defaultdict


class AdjacencyGraph(object):
    """Adjacency Graph on which to perform Swendsen-Wang Cuts."""
    def __init__(self, size, edges):
        super(AdjacencyGraph, self).__init__()

        self.size = size
        self.edges = edges

        #self.adj_list = defaultdict(list)
        #for (start, end) in edges:
        #    try:
        #        assert(start in range(0, size) and end in range(0, size))
        #    except AssertionError:
        #        raise ValueError('More vertex given than the size of the graph.')
        #    self.adj_list[start].append(end)
        return


class SWCuts(object):
    """Swendsen-Wang cuts."""
    def __init__(self):
        super(SWCuts, self).__init__()

    def sample(self, adjacency_graph, edge_prob_func, target_evaluation_func):
        self.current_state = adjacency_graph

        self.adjacency_graph = adjacency_graph
        # Cache turn-on probability of each edge and stored in a adjacent list.
        self.edge_on_prob = __cache_turn_on_probabilities(
            adjacency_graph, edge_prob_func)

        while not self.__has_converged():
            # Form connected components over the whole space.
            connected_components = self.__form_connected_components(entire_space=True)

            # Flip the connect components probabilistically.
            self.current_state = self.__flip_connected_components(
                connected_components, target_evaluation_func)
        return

    def __cache_turn_on_probabilities(self, adjacency_graph, edge_prob_func):
        """Store turn-on probability of each edge in a adjacent list."""
        edges_on_prob = defaultdict(dict)
        for (s, t) in adjacency_graph.edges:
            edges_on_prob[s][t] = edge_prob_func(s, t)
        return edges_on_prob

    def __has_converged(self):
        """Convergence Test."""
        return

    def __form_connected_components(self, entire_space=True):
        """Form connected components (CPs) probabilistically.
        All CPs are formed on the entire space if entire_space=True,
        Otherwise only one CP will be formed from a random vertex.

        This function return a list of CP. Each CP is a list of vertexes."""
        size = self.adjacency_graph.size

        if entire_space:
            # Form CPs by DFS.
            pass
        else:
            pass

    def __flip_connected_components(self, target_evaluation_func):
        newstate = self.current_state
        return newstate
