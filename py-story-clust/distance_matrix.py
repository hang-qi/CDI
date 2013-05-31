import datetime
import math
import logging

import matplotlib.pyplot as plt
import numpy as np
from numpy.matlib import zeros
import scipy.cluster.vq as clust

from sklearn.manifold import MDS
from sklearn.cluster import KMeans, mean_shift

from vocabulary import vocabulary
from cooccurrence.cooccur_mat import CooccurMatrix
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

def md_scaling(cooccur_matrix):
    distance_matrix = -np.log(cooccur_matrix.matrix)

    mds = MDS(dissimilarity='precomputed')
    mds.fit(distance_matrix)
    return mds.embedding_


def cluster(points, labels=None):
    #km = KMeans(n_clusters=3, init='k-means++', max_iter=100, n_init=1,
    #            verbose=1)
    #km.fit(points)
    return mean_shift(points)


def plot_points(points, labels=None, cluster_labels=None):
    cluster_style = ['or', 'ob', 'og', 'oc', 'om', 'oy', 'ok']
    style = '.r'
    for idx, points in enumerate(points):
        if cluster_labels is not None:
            style = cluster_style[cluster_labels[idx] % 7]
        plt.plot(points[0], points[1], style)
        if not labels is None:
            plt.text(points[0], points[1], labels[idx], fontsize=10)


def main():
    logging.basicConfig(level=logging.INFO)

    # load similarity matrix
    mat = CooccurMatrix()
    mat.load('mat/similarity_np2')
    points = md_scaling(mat)
    (center, labels) = cluster(points)

    # plot the points with label
    plot_points(points, labels=mat.vocabulary.word_list, cluster_labels=labels)
    plt.show()


if __name__ == '__main__':
    main()
