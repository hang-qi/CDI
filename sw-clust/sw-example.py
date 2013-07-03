# This is a toy example of SW-Cuts.
from algorithm import sw


class Model:
    def __init__(self):
        self.edge = 0.5

    def edge_func(self, s, t):
        return self.edge

    def target_func(self, labeling):
        if labeling[0] == labeling[1] == labeling[2]:
            return 1
        else:
            return 0.1


def intermediate_callback(labeling):
    intermediate_callback.iteration += 1
    print 'Iteration {0:4d}:\t {1}'.format(intermediate_callback.iteration, labeling)
intermediate_callback.iteration = 0


def main():
    m = Model()
    graph_size = 3
    edges = [(0, 1), (1, 2)]
    sw.sample(graph_size, edges, m.edge_func, m.target_func, intermediate_callback)
    return


if __name__ == '__main__':
    main()
