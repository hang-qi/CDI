# The whole SW Process
from algorithm import sw
from preprocessing import readingfiles
from statistics.statistics import Statistics

import matplotlib.pyplot as plt


class Plotter(object):
    def __init__(self, stat, true_segment, true_eval):
        self.iterations = []
        self.energies = []
        self.stat = stat
        self.true_segment = true_segment
        self.true_eval = true_eval

        # You probably won't need this if you're embedding things in a tkinter plot...
        plt.ion()
        self.fig = plt.figure(figsize=(16, 10))
        self.energy_plot = self.fig.add_subplot(211)
        self.segment_plot = self.fig.add_subplot(212)

    def plot_callback(self, current_labeling, context):
        print(current_labeling)

        self.iterations.append(context.iteration_counter)
        self.energies.append(self.stat.target_evaluation_func(current_labeling))

        # energy plot
        self.energy_plot.clear()
        self.energy_plot.plot(self.iterations, self.energies)
        self.energy_plot.hold(True)
        self.energy_plot.plot(self.iterations, [self.true_eval]*len(self.iterations), 'r')

        # segmentation plot
        self.segment_plot.clear()
        self.segment_plot.plot(self.true_segment.seg_boundary, [2]*len(self.true_segment.seg_boundary), '.r')
        self.segment_plot.hold(True)
        current_seg = []
        for i in range(1, len(current_labeling)):
            if current_labeling[i] != current_labeling[i-1]:
                current_seg.append(i)
        self.segment_plot.plot(current_seg, [1]*len(current_seg), '.')
        self.segment_plot.axis([0, self.stat.all_nodes.node_num, 0, 3])

        self.fig.canvas.draw()


def SW_Process():
    [all_nodes, true_segment, class_num, np1_voc, vp_voc, np2_voc, np1_prob, vp_prob, np2_prob, class_prior_prob, transition_prob] = readingfiles.preprocessing('2008081519', 'preprocessing/model_segmenter.txt')
    print('Reading Files Finished')
    print('Calculate Probability Given Category for Each Node')
    all_nodes.set_nodes_prob(class_num, np1_voc, vp_voc, np2_voc, np1_prob, vp_prob, np2_prob)

    node_number = all_nodes.node_num
    edges = []
    for i in range(0, node_number-1):
        j = i + 1
        edges.append([i, j])

    stat = Statistics(all_nodes, class_num, np1_voc, vp_voc, np2_voc, np1_prob, vp_prob, np2_prob, class_prior_prob, transition_prob)
    true_eval = stat.calculate_ground_truth(true_segment)
    plotter = Plotter(stat, true_segment, true_eval)

    initial_labeling = []
    for i in range(0, node_number):
        initial_labeling.append(i % 2)

    print('Start Sampling')
    sw.sample(node_number, edges, stat.calculate_Qe, stat.target_evaluation_func, plotter.plot_callback, initial_labeling=None)


def main():
    SW_Process()


if __name__ == '__main__':
    main()
