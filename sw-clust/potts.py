# The whole SW Process
from algorithm import sw
from model import segment
from model.nodes import Node, Nodes
from preprocessing import readingfiles
from statistics.statistics import Statistics
import math

import matplotlib.pyplot as plt

N = 64

edges = []
for i in range(0, N):
    for j in range(0, N):
        current_v = i * N + j
        assert(current_v < N*N)
        if j < (N-1):
            right_v = i * N + j + 1
            assert(right_v < N*N)
            edges.append((current_v, right_v))

        if i < (N-1):
            down_v = (i+1) * N + j
            assert(down_v < N*N)
            edges.append((current_v, down_v))


class Model(object):
    def __init__(self):
        beta = 0.5
        self.prob_on = 1.0 - math.exp(-beta)
        pass

    def edge_prob(self, s, t, context):
        return self.prob_on * (context.current_labeling[s] == context.current_labeling[t])

    def target_prob(self, labeling):
        # uniform
        return 1.0

    def statistics(self, labeling):
        h = 0.0
        for (s, t) in edges:
            if (labeling[s] != labeling[t]):
                h += 1
        h = h / (2*N*N)
        return h


class Plotter(object):
    def __init__(self, model):
        self.iterations = []
        self.energies = []
        self.model = model

        # You probably won't need this if you're embedding things in a tkinter plot...
        plt.ion()
        self.fig = plt.figure()
        self.energy_plot = self.fig.add_subplot(111)

    def plot_callback(self, current_labeling, context):
        print(current_labeling)

        self.iterations.append(context.iteration_counter)
        self.energies.append(self.model.statistics(current_labeling))

        self.energy_plot.clear()
        self.energy_plot.plot(self.iterations, self.energies)
        self.fig.canvas.draw()


def SW_Process():
    node_number = N*N

    model = Model()
    plotter = Plotter(model)

    initial_labeling = []
    for i in range(0, node_number):
        initial_labeling.append(i % 2)
    #initial_labeling = None

    print('Start Sampling')
    sw.sample(node_number, edges, model.edge_prob, model.target_prob, plotter.plot_callback, initial_labeling=initial_labeling, max_labels=2)


def main():
    SW_Process()


if __name__ == '__main__':
    main()
