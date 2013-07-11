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

import mpmath


def sample(graph_size, edges, edge_prob_func, target_eval_func, intermediate_callback=None, initial_labeling=None, monitor_statistics=None, max_labels=None):
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
        target_eval_func(labeling, context)

- intermediate_callback (optional):
    this function will be called with current labeling result at
    the end of every iteration.
        callback(labeling)

- inital_labeling (optional):
    the initial status to begin from.
    All vertex will have the save initial label if not provided.

- max_labels (optional):
    the max number of labels can be used.
    Each vertex can have its own unique label if max_labels is not specified.

"""
    sw = _SWCuts()
    return sw.sample(
        _AdjacencyGraph(graph_size, edges),
        edge_prob_func,
        target_eval_func,
        intermediate_callback=intermediate_callback,
        initial_labeling=initial_labeling,
        monitor_statistics_func=monitor_statistics,
        max_labels=max_labels)


class SWContext(object):
    def __init__(self):
        self.iteration_counter = 0
        self.current_clustering = []

    def count_iteration(self):
        self.iteration_counter += 1

    def set_result(self, current_clustering):
        self.current_clustering = current_clustering


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


class _ConvergenceMonitor(object):
    def __init__(self, monitor_func, epsilon=0, stationary_steps=500):
        self.__monitor_statistics_func = monitor_func
        self.__epsilon = epsilon
        self.__stationary_steps = stationary_steps
        self.__history = []
        self.__window = (0, 0)

    def has_converged(self, context):
        if self.__monitor_statistics_func is None:
            return False

        current_statistics = self.__monitor_statistics_func(context.current_clustering)
        # record history
        self.__history.append(current_statistics)
        # adjust convergence window
        self.__window = (self.__window[0], len(self.__history) - 1)

        values_in_window = self.__history[self.__window[0]: self.__window[1]+1]
        while max(values_in_window) - min(values_in_window) > self.__epsilon:
            self.__window = (self.__window[0]+1, self.__window[1])
            values_in_window = self.__history[self.__window[0]: self.__window[1]+1]

        if self.__window[1]-self.__window[0] < self.__stationary_steps:
            return False
        else:
            return True


class _SWCuts(object):
    """Swendsen-Wang cuts."""
    def __init__(self):
        super(_SWCuts, self).__init__()
        self.context = SWContext()

    def sample(self, adjacency_graph, edge_prob_func, target_eval_func, intermediate_callback=None, initial_labeling=None, monitor_statistics_func=None, max_labels=None):
        # Initial labeling.
        if initial_labeling is not None:
            current_clustering = initial_labeling
        else:
            current_clustering = [set(range(0, adjacency_graph.size))]

        self.adjacency_graph = adjacency_graph
        if max_labels is not None:
            self.max_labels = max_labels
        else:
            self.max_labels = self.adjacency_graph.size

        # Functions
        self.edge_prob_func = edge_prob_func
        self.target_eval_func = target_eval_func
        self.convergence_monitor = _ConvergenceMonitor(monitor_statistics_func)

        self.context.set_result(current_clustering)

        while not self.__has_converged():
            self.context.count_iteration()
            self.context.set_result(current_clustering)

            # Determine edge status (on or off) probabilistically.
            edge_status = self.__determine_edge_status()

            # Form connected components over the whole space.
            connected_components = self.__form_connected_components(
                current_clustering, edge_status)

            # Do a sweep
            #for component in connected_components:
            component = connected_components[random.randint(0, len(connected_components)-1)]
            # Flip the connect component probabilistically.
            current_clustering = self.__flip_connected_component(
                current_clustering, component)
            self.context.set_result(current_clustering)

            # Propagate intermediate result if has callback function.
            if intermediate_callback is not None:
                intermediate_callback(copy.copy(current_clustering), self.context)

        return current_clustering

    def __has_converged(self):
        """Convergence Test."""
        return self.convergence_monitor.has_converged(self.context)

    def __edge_on_probability(self, s, t):
        # Ensure s < t
        if s > t:
            s, t = t, s
        return self.edge_prob_func(s, t, self.context)

    def __determine_edge_status(self):
        edge_status = defaultdict(dict)
        for (s, t) in self.adjacency_graph.edges:
            # Determine the status of each edge probabilistically.
            # Turn edge 'on' if r < prob(on), 'off' otherwise.
            r = random.random()
            if (r < self.__edge_on_probability(s, t)):
            #if (r < self.edge_prob_func(s, t, self.context)):
                edge_status[s][t] = True
                edge_status[t][s] = True
            else:
                edge_status[s][t] = False
                edge_status[t][s] = False
        return edge_status

    def __form_connected_components(self, current_clustering, edge_status):
        """Form connected components (CP) probabilistically.
        This function returns a list of CPs.
        Each CP is a list of vertexes. And cut_edges is a list of edges, i.e. [(s, t)]."""
        size = self.adjacency_graph.size
        visited = [False for v in range(0, size)]

        connected_components = []
        for cluster in current_clustering:
            for v in cluster:
                if not visited[v]:
                    seed_vertex = v
                    # Form one CP from a random vertex
                    #seed_vertex = random.randint(0, size-1)
                    component = self.__grow_component_by_bfs(
                        seed_vertex, cluster, edge_status, visited)
                    connected_components.append(component)

        return connected_components

    def __grow_component_by_bfs(self, seed_vertex, seed_cluster, edge_status, visited):
        component = set()
        d = deque([seed_vertex])
        while(len(d) != 0):
            v = d.popleft()
            if visited[v]:
                continue

            visited[v] = True
            component.add(v)

            # Add all connected vertex into the queue.
            for u in self.adjacency_graph.adj_list[v]:
                if u in seed_cluster:
                    if edge_status[v][u]:
                        d.append(u)
        return component

    def __flip_connected_component(self, current_clustering, component):
        # Possible labels for for connected component:
        #   - Label of any neighbors, so that the CP will be merged into a neighbor.
        #   - New label, so that the CP will be a new cluster.

        # Find candidate labels from neighbors

        cluster_dict = dict()
        for (cluster_index, cluster) in enumerate(current_clustering):
            for v in cluster:
                cluster_dict[v] = cluster_index

        for v in component:
            host_cluster_index = cluster_dict[v]
            break

        neighbor_clusters = set()
        cut_edges_dict = defaultdict(set)

        for v in component:
            for u in self.adjacency_graph.adj_list[v]:
                if u not in component:
                    neighbor_cluster_index = cluster_dict[u]
                    neighbor_clusters.add(neighbor_cluster_index)
                    cut_edges_dict[neighbor_cluster_index].add((v, u))

        # Generate candidates
        # 1. Add all vertex in component to one of the neighbor
        #    and remove from host cluster.
        candidates = []
        for neighbor_cluster_index in neighbor_clusters:
            candidate = copy.deepcopy(current_clustering)
            candidate[neighbor_cluster_index].union(component)
            if current_clustering[host_cluster_index] == component:
                candidate.remove(component)
            else:
                candidate[host_cluster_index] -= component
            candidates.append((candidate, cut_edges_dict[neighbor_cluster_index]))

        # 2. As a new cluster
        new_candidate = copy.deepcopy(current_clustering)
        if current_clustering[host_cluster_index] == component:
            new_candidate.append(new_candidate)
        else:
            new_candidate[host_cluster_index] -= component
            new_candidate.append(component)
        candidates.append(new_candidate, set())

        posteriors = []
        denominator = mpmath.mpf(0.0)
        for (candidate, cut_set) in candidates:
            # This weighted posterior guarantees the detailed balance.
            weight = mpmath.mpf(1.0)
            for (s, t) in cut_set:
                weight *= (1 - self.__edge_on_probability(s, t))
            val = mpmath.mpf(self.target_eval_func(candidate, self.context))
            posterior = weight * val

            posteriors.append(posterior)
            denominator += posterior

        # Normalize the posterior probability.
        assert(denominator != 0)
        posteriors = [p/denominator for p in posteriors]

        print('Posteriors: {0}'.format(posteriors))
        print('Component: {0}'.format(component))
        print('# of candidate: {0}'.format(len(candidates)))

        # Sample from the posterior probability.
        cdf = [sum(posteriors[0:x]) for x in range(1, len(posteriors)+1)]
        r = random.random()
        for i in range(0, len(cdf)):
            if cdf[i] > r:
                return candidates[i]
