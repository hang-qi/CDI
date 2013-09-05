# The whole SW Process
import matplotlib.pyplot as plt

from algorithm import sw
from preprocessing import readingfiles
from model.classifier import Classifier
from model.segmentation_model import SegmentationModel


class Plotter(object):
    def __init__(self, segmentation_model, true_segment):
        self.iterations = []
        self.energies = []
        self.temperatures = []
        self.segmentation_model = segmentation_model
        self.true_segment = true_segment

        self.pronoun = []
        for i in range(0, len(self.segmentation_model.all_sentences)):
            if self.segmentation_model.all_sentences[i].pronoun:
                self.pronoun.append(i)
        self._true_eval = self.segmentation_model.calculate_energy(true_segment)

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
        self.energies.append(self.segmentation_model.calculate_energy(current_labeling))
        self.temperatures.append(self.segmentation_model.cooling_schedule(context.iteration_counter))

        # energy plot
        self.energy_plot.clear()
        self.energy_plot.set_title('Energy')
        self.energy_plot.plot(self.iterations, self.energies)
        self.energy_plot.hold(True)
        self.energy_plot.plot([1, len(self.iterations)], [self._true_eval, self._true_eval], 'r')

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
        self.segment_plot.axis([0, len(self.segmentation_model.all_sentences), 0, 3])
        #self.segment_plot.hold(True)
        #self.segment_plot.plot(self.pronoun, [1.5]*len(self.pronoun), '.')

        self.fig.canvas.draw()

    def save(self):
        self.fig.savefig('plot.png', transparent=False, bbox_inches=None, pad_inches=0.1)


def sw_Process():
    [all_sentences, true_segment] = readingfiles.read_testing_file('2008080814')
    [transition_prob, length_prior, seg_num_prior] = readingfiles.load_model_parameters('preprocessing/model_segmenter.txt')
    classifier = Classifier('preprocessing/model_segmenter.txt')

    segmentation_model = SegmentationModel(all_sentences, transition_prob, length_prior, seg_num_prior, classifier)
    plotter = Plotter(segmentation_model, true_segment)

    node_number = len(all_sentences)
    edges = []
    for i in range(0, node_number-1):
        j = i + 1
        edges.append([i, j])

    print('Start Sampling')
    sw.sample(node_number, edges, segmentation_model.calculate_Qe, segmentation_model.target_evaluation_func, plotter.plot_callback, initial_clustering=None, monitor_statistics=segmentation_model.calculate_energy)
    print('Converged.')
    plotter.save()


def main():
    sw_Process()


if __name__ == '__main__':
    main()
