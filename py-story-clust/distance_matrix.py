import datetime
import math
import logging
import glob

import matplotlib.pyplot as plt
import numpy as np
from numpy.matlib import zeros
import scipy.cluster.vq as clust

from sklearn.manifold import MDS
from sklearn.cluster import KMeans, mean_shift

from vocabulary import vocabulary
from cooccurrence.cooccur_mat import CooccurMatrix
from cooccurrence import cluster_triplets
from storyclustering import storyclustering

# Conversion between similarity matrix and distance matrix
# similarity_matrix = np.exp(-distance_matrix / distance_matrix.std())
# distance_matrix = np.log(similarity_matrix)


def plot_cities():
    #distance_matrix = get_distances()
    cities = 'BOS     CHI     DC      DEN     LA      MIA     NY      SEA     SF'.split()
    distance_matrix = np.array([
        [0   , 963 , 429 , 1949, 2979, 1504, 206 , 2976, 3095],
        [963 , 0   , 671 , 996 , 2054, 1329, 802 , 2013, 2142],
        [429 , 671 , 0   , 1616, 2631, 1075, 233 , 2684, 2799],
        [1949, 996 , 1616, 0   , 1059, 2037, 1771, 1307, 1235],
        [2979, 2054, 2631, 1059, 0   , 2687, 2786, 1131, 379],
        [1504, 1329, 1075, 2037, 2687, 0   , 1308, 3273, 3053],
        [206 , 802 , 233 , 1771, 2786, 1308, 0   , 2815, 2934],
        [2976, 2013, 2684, 1307, 1131, 3273, 2815, 0   , 808],
        [3095, 2142, 2799, 1235, 379 , 3053, 2934, 808 , 0]
        ])

    # assert symmetric
    for (i, j) in [(i, j) for i in range(0, 8) for j in range(0, 8)]:
        try:
            assert(distance_matrix[i][j] == distance_matrix[j][i])
        except AssertionError:
            print((i, j))

    print(distance_matrix)
    mds = MDS(dissimilarity='precomputed')
    mds.fit(distance_matrix)
    print(mds.embedding_)
    for idx, points in enumerate(mds.embedding_):
        plt.plot(points[0], points[1], 'r.')
        plt.text(points[0], points[1], cities[idx])
    plt.show()
    return


def md_scaling(co_matrix, is_distance_matrix=False):
    if not is_distance_matrix:
        distance_matrix = -np.log(co_matrix.matrix)
    else:
        distance_matrix = co_matrix

    mds = MDS(dissimilarity='precomputed')
    mds.fit(distance_matrix)
    return mds.embedding_


def cluster(points, labels=None):
    #km = KMeans(n_clusters=3, init='k-means++', max_iter=100, n_init=1,
    #            verbose=1)
    #km.fit(points)
    return mean_shift(points)


def plot_points(points, ground_truth_labels=None, cluster_labels=None):
    cluster_style = ['or', 'ob', 'og', 'oc', 'om', 'oy', 'ok']
    style = '.r'
    for idx, points in enumerate(points):
        if cluster_labels is not None:
            style = cluster_style[cluster_labels[idx] % 7]
        plt.plot(points[0], points[1], style)
        if not ground_truth_labels is None:
            plt.text(points[0], points[1], ground_truth_labels[idx], fontsize=10)


def cluster_and_plot(co_mat, is_distance_matrix=False, ground_truth_labels=None, figure_title=None, save_figure_filename=None, show_figure=True):
    # Perform multidimensional scaling to map to 2D space.
    points = md_scaling(co_mat, is_distance_matrix)

    # Clustering.
    (center, cluster_labels) = cluster(points)

    # Plot the points with label and save.
    plt.figure()
    plot_points(points, ground_truth_labels=ground_truth_labels, cluster_labels=cluster_labels)

    if figure_title is not None:
        plt.title(figure_title)
    if save_figure_filename is not None:
        plt.savefig(save_figure_filename, bbox_inches=0)
    if show_figure:
        plt.show()


def create_words_map_for_stories(triplets_files):
    for triplet_file in triplets_files:
        logging.debug('Generating similarity for {0}'.format(triplet_file))

        # generate similarity matrix for each of the story.
        co_mat = cluster_triplets.learn_triplets_cooccur_mat(triplet_file, 'mat/np1_co_mat')

        # save the similarity matrix in individual files.
        try:
            fig_filename = 'fig/{0}.png'.format(triplet_file.split('/')[-1] + '_np1')
            cluster_and_plot(
                co_mat.matrix,
                ground_truth_labels=co_mat.vocabulary.word_list,
                save_figure_filename=fig_filename,
                show_figure=False)
        except Exception:
            logging.warning('Cluster cannot be found.')
            pass
    return


def main():
    logging.basicConfig(level=logging.DEBUG)
    #
    # Plot a word map for each story.
    #
    #triplets_files = glob.glob('triplet_files/*.txt')
    #triplets_files.sort()
    #create_words_map_for_stories(triplets_files)

    #
    # Plot a story map for the corpus.
    #
    (dist, ground_truth) = storyclustering.learn_story_distances('triplet_files/[124]_*.txt', 'mat/np1_co_mat', min_similarity=0.8)
    cluster_and_plot(dist, is_distance_matrix=True, ground_truth_labels=ground_truth)

    return

if __name__ == '__main__':
    main()
