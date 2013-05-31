import datetime
import math
import logging

import numpy as np
from numpy.matlib import zeros
import networkx as nx

import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import linkage, dendrogram
from scipy.cluster import hierarchy as hier

from sklearn.cluster import DBSCAN
from sklearn import metrics
from sklearn.datasets.samples_generator import make_blobs
from sklearn.preprocessing import StandardScaler


def main():
    logging.basicConfig(level=logging.INFO)

    #distance_matrix = get_distances()
    distance_matrix = np.matrix([
        [0, 206, 429, 1504, 963, 2976, 3095, 2979, 1949],
        [206, 0, 233, 1308, 802, 1815, 2934, 2786, 1771],
        [4289, 233, 0, 1075, 671, 2684, 2799, 2631, 1616],
        [1504, 1308, 1075, 0, 1329, 3273, 3053, 2687, 2037],
        [963, 802, 671, 1329, 0, 2013, 2142, 2054, 996],
        [2976, 2815, 2684, 3273, 2013, 0, 808, 1131, 1307],
        [3095, 2934, 2799, 3053, 2142, 808, 0, 379, 1235],
        [2979, 2786, 2631, 2687, 2054, 1131, 379, 0, 1059],
        [1949, 1771, 1616, 2037, 996, 1307, 1235, 1059, 0]])
    print(distance_matrix)

    # similarity = np.exp(-distance_matrix / distance_matrix.std())
    # distance = - log (similarity)

    labels = 'BOST NY DC MIAM CHIC SEAT SF LA DENV'.split()
    print(labels)
    clusters = linkage(distance_matrix, method='single', metric='euclidean')
    dendrogram(clusters, labels=labels)
    idx = hier.fcluster(clusters, 0.5*distance_matrix.max(), 'distance')
    print(idx)
    plt.show()


if __name__ == '__main__':
    main()
