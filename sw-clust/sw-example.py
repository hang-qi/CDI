# This is a toy example of SW-Cuts.
from algorithm.sw import AdjacencyGraph, SWCuts


def edge_func(s, t):
    return 0.5


def target_func(labeling):
    if labeling[0] == labeling[1] == labeling[2]:
        return 1
    else:
        return 0.1


def intermediate_callback(labeling):
    intermediate_callback.iteration += 1
    print 'Iteration {0:4d}:\t {1}'.format(intermediate_callback.iteration, labeling)
intermediate_callback.iteration = 0


def main():
    graph = AdjacencyGraph(3, [(0, 1), (1, 2)])
    swcut = SWCuts()
    swcut.sample(graph, edge_func, target_func, intermediate_callback)
    return


if __name__ == '__main__':
    main()
