"""
The implementation of Swendsen-Wang Cuts algorithm for clustering.

Usage:
        import sw
        labeling = sw.sample(...)

    See sample() function for details.
"""

from collections import defaultdict
from collections import deque
import copy
import random


def sample(graph_size, edges, edge_prob_func, target_eval_func, intermediate_callback=None):
    """Generating fair samples by Swendsen-Wang Cuts.
Parameters:
- graph_size:
    number of nodes in the adjacency graph.

- edges:
    edges in the adjacency graph. This shall be a list of edges,
    where each edge is expressed as a tuple of two end points.
        e.g. [(0, 2), (1, 2), (2, 3)]

- edge_prob_func:
    the callback function which calculates the probability of
    turning on edges (s, t). This function shall be in the
    following form:
        edge_func(s, t)

- target_eval_func:
    the callback function which evaluates the probability of a
    cluster labeling. This probability does not need to be normalized.
    MCMC theory guarantees that fair samples will be generated from
    this target distribution when the chain converges.
        target_eval_func(labeling)

- intermediate_callback (optional):
    this function will be called with current labeling result at
    the end of every iteration.
        callback(labeling)
"""
    sw = _SWCuts()
    return sw.sample(
        _AdjacencyGraph(graph_size, edges), edge_prob_func, target_eval_func, intermediate_callback)


class _AdjacencyGraph(object):
    """Adjacency Graph on which to perform Swendsen-Wang Cuts."""
    def __init__(self, size, edges):
        """size is a integer.
        Edges is a list of edge tuples. i.e. [ (s, t) ]. """
        super(_AdjacencyGraph, self).__init__()

        self.size = size
        self.edges = set()
        self.adj_list = defaultdict(list)

        for (start, end) in edges:
            if start > end:
                start, end = end, start
            self.edges.add((start, end))
            try:
                assert(start in range(0, size) and end in range(0, size))
            except AssertionError:
                raise ValueError('More vertex given than the size of the graph.')
            self.adj_list[start].append(end)
            self.adj_list[end].append(start)
        return


class _SWCuts(object):
    """Swendsen-Wang cuts."""
    def __init__(self):
        super(_SWCuts, self).__init__()

    def sample(self, adjacency_graph, edge_prob_func, target_eval_func, intermediate_callback=None):
        # Initial labeling.
        # current_labeling = [0] * adjacency_graph.size
        current_labeling = []
        for i in range(0, adjacency_graph.size):
            current_labeling.append(i%2)


        self.adjacency_graph = adjacency_graph
        self.max_labels = adjacency_graph.size

        # Cache turn-on probability of each edge and stored in a adjacent list.
        # Since the edge probability only concern the two end point of the edge,
        # this probability will remain the same during the run.
        self.__cache_turn_on_probability_func(edge_prob_func)

        while not self.__has_converged():
            # Determine edge status (on or off) probabilistically.
            edge_status = self.__determine_edge_status()

            # Form connected components over the whole space.
            connected_component = self.__form_connected_component(
                current_labeling, edge_status)

            # Flip the connect components probabilistically.
            current_labeling = self.__flip_connected_component(
                current_labeling, connected_component, target_eval_func)

            # Propagate intermediate result if has callback function.
            if intermediate_callback is not None:
                intermediate_callback(copy.copy(current_labeling))

        return current_labeling

    def __has_converged(self):
        """Convergence Test."""
        return False

    def __cache_turn_on_probability_func(self, edge_prob_func):
        """Store turn-on probability of each edge in a adjacent list."""
        self.__edge_on_prob_cache = defaultdict(dict)
        for (s, t) in self.adjacency_graph.edges:
                self.__edge_on_prob_cache[s][t] = edge_prob_func(s, t)

    def __edge_on_probability(self, s, t):
        # Ensure s < t
        if s > t:
            s, t = t, s
        return self.__edge_on_prob_cache[s][t]

    def __determine_edge_status(self):
        edge_status = defaultdict(dict)
        for (s, t) in self.adjacency_graph.edges:
            # Determine the status of each edge probabilistically.
            # Turn edge 'on' if r < prob(on), 'off' otherwise.
            r = random.random()
            if (r < self.__edge_on_probability(s, t)):
                edge_status[s][t] = True
                edge_status[t][s] = True
            else:
                edge_status[s][t] = False
                edge_status[t][s] = False
        return edge_status

    def __form_connected_component(self, current_labeling, edge_status):
        """Form a connected component (CP) probabilistically from a random vertex.
        This function returns a tuple (CP, cut_edges).
        CP is a list of vertexes. And cut_edges is a list of edges, i.e. [(s, t)]."""
        size = self.adjacency_graph.size
        visited = [False for v in range(0, size)]

        # Form one CP from a random vertex
        random_vertex = random.randint(0, size-1)
        (component, cut_edges) = self.__grow_component_by_bfs(
            random_vertex, current_labeling, edge_status, visited)
        return (component, cut_edges)

    def __grow_component_by_bfs(self, start_vertex, current_labeling, edge_status, visited):
        component = []
        cut_edges = []
        original_label = current_labeling[start_vertex]
        d = deque([start_vertex])
        while(len(d) != 0):
            v = d.popleft()
            if visited[v]:
                continue

            visited[v] = True
            component.append(v)

            # Add all connected vertex into the queue.
            for u in self.adjacency_graph.adj_list[v]:
                if current_labeling[u] == original_label:
                    if edge_status[v][u]:
                        d.append(u)
                    else:
                        cut_edges.append((v, u))
        cut_edges = [(s, t) for (s, t) in cut_edges if not (s in component and t in component)]
        return (component, cut_edges)

    def __flip_connected_component(self, current_labeling, connected_component, target_eval_func):
        (component, cut_edges) = connected_component

        # Possible labels for for connected component:
        #   - Label of any neighbors, so that the CP will be merged into a neighbor.
        #   - New label, so that the CP will be a new cluster.

        # Find candidate labels from neighbors
        candidate_labels = set()
        cut_edges_dict = defaultdict(set)
        for v in component:
            for u in self.adjacency_graph.adj_list[v]:
                if u not in component:
                    candidate_label = current_labeling[u]
                    candidate_labels.add(candidate_label)
                    cut_edges_dict[candidate_label].add((v, u))
        # New label
        for label in range(0, self.max_labels):
            if label not in candidate_labels:
                candidate_labels.add(label)
                cut_edges_dict[label] = set()
                break

        # Compute posterior probability of each candidate.
        labeling_candidates = []
        posteriors = []
        denominator = 0.0
        for label in candidate_labels:
            labeling = copy.copy(current_labeling)
            for v in component:
                labeling[v] = label

            # This weighted posterior guarantees the detailed balance.
            weight = 1.0
            for (s, t) in cut_edges_dict[label]:
                weight *= (1 - self.__edge_on_probability(s, t))
            val = target_eval_func(labeling)
            print(val)
            posterior = weight * val


            labeling_candidates.append(labeling)
            posteriors.append(posterior)
            denominator += posterior
        # Normalize the posterior probability.
        posteriors = [p/denominator for p in posteriors]

        # Sample from the posterior probability.
        cdf = [sum(posteriors[0:x]) for x in range(1, len(posteriors)+1)]
        r = random.random()
        for i in range(0, len(cdf)):
            if cdf[i] > r:
                return labeling_candidates[i]
