# The whole SW Process
from algorithm import sw
from preprocessing import readingfiles
from model.segmentation_model import SegmentationModel

import matplotlib.pyplot as plt


class Plotter(object):
    def __init__(self, stat, true_segment, true_eval):
        self.iterations = []
        self.energies = []
        self.temperatures = []
        self.stat = stat
        self.true_segment = true_segment
        self.true_eval = true_eval
        self.pronoun = []
        for i in range(0, self.stat.all_nodes.node_num):
            if self.stat.all_nodes.nodes[i].pronoun:
                self.pronoun.append(i)

        # You probably won't need this if you're embedding things in a tkinter plot...
        plt.ion()
        self.fig = plt.figure(figsize=(16, 10))
        #self.energy_plot = self.fig.add_subplot(211)
        #self.segment_plot = self.fig.add_subplot(212)
        self.energy_plot = self.fig.add_subplot(plt.subplot2grid((2, 3), (0, 0), colspan=2))
        self.temperature_plot = self.fig.add_subplot(plt.subplot2grid((2, 3), (0, 2)))
        self.segment_plot = self.fig.add_subplot(plt.subplot2grid((2, 3), (1, 0), colspan=3))

    def plot_callback(self, current_labeling, context):
        print(current_labeling)

        self.iterations.append(context.iteration_counter)
        self.energies.append(self.stat.calculate_energy(current_labeling))
        self.temperatures.append(self.stat.cooling_schedule(context.iteration_counter))

        # energy plot
        self.energy_plot.clear()
        self.energy_plot.set_title('Energy')
        self.energy_plot.plot(self.iterations, self.energies)
        self.energy_plot.hold(True)
        self.energy_plot.plot([1, len(self.iterations)], [self.true_eval, self.true_eval], 'r')

        # temperature plot
        self.temperature_plot.clear()
        self.temperature_plot.set_title('Temperature')
        self.temperature_plot.plot(self.iterations, self.temperatures)

        # segmentation plot
        current_seg = [max(x)+1 for x in current_labeling]
        self.segment_plot.clear()
        self.segment_plot.set_title('Segmentation')
        seg_boundary = [max(x)+1 for x in self.true_segment]
        self.segment_plot.plot(seg_boundary, [2]*len(seg_boundary), '.r')
        self.segment_plot.hold(True)
        self.segment_plot.plot(current_seg, [1]*len(current_seg), '.')
        self.segment_plot.axis([0, self.stat.all_nodes.node_num, 0, 3])
        #self.segment_plot.hold(True)
        #self.segment_plot.plot(self.pronoun, [1.5]*len(self.pronoun), '.')

        self.fig.canvas.draw()

    def save(self):
        self.fig.savefig('plot.png', transparent=False, bbox_inches=None, pad_inches=0.1)


def SW_Process():
    [all_nodes, true_segment, class_num, np1_voc, vp_voc, np2_voc, np1_prob, vp_prob, np2_prob, class_prior_prob, transition_prob, length_prior, seg_num_prior] = readingfiles.preprocessing('2008080814', 'preprocessing/model_segmenter.txt')
    print('Reading Files Finished')
    print('Calculate Probability Given Category for Each Node')
    all_nodes.set_nodes_prob(class_num, np1_voc, vp_voc, np2_voc, np1_prob, vp_prob, np2_prob)

    node_number = all_nodes.node_num
    edges = []
    for i in range(0, node_number-1):
        j = i + 1
        edges.append([i, j])

    stat = SegmentationModel(all_nodes, class_num, np1_voc, vp_voc, np2_voc, np1_prob, vp_prob, np2_prob, class_prior_prob, transition_prob, length_prior, seg_num_prior)
    true_eval = stat.calculate_energy(true_segment)
    plotter = Plotter(stat, true_segment, true_eval)

    #initial_labeling = []
    #seglabel = 0
    #for i in range(0, node_number):
    #    if all_nodes.nodes[i].pronoun:
    #        initial_labeling.append(seglabel)
    #    else:
    #        seglabel = 1 - seglabel
    #        initial_labeling.append(seglabel)
    #    #initial_labeling.append(0)

    print('Start Sampling')
    sw.sample(node_number, edges, stat.calculate_Qe, stat.target_evaluation_func, plotter.plot_callback, initial_clustering=None, monitor_statistics=stat.calculate_energy)
    print('Converged.')
    plotter.save()


def main():
    SW_Process()


if __name__ == '__main__':
    main()
