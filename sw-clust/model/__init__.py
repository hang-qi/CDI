import numpy as np


# constants
NUM_WORD_TYPE = 3
WORD_TYPE_NP1 = 0
WORD_TYPE_VP = 1
WORD_TYPE_NP2 = 2
WORD_TYPES = [WORD_TYPE_NP1, WORD_TYPE_VP, WORD_TYPE_NP2]


def calculate_tv_norm(dist1, dist2):
    assert(np.shape(dist1) == np.shape(dist2))
    diff = dist1 - dist2
    diff = np.asarray(diff, dtype=np.float)
    diff = np.absolute(diff)
    return np.sum(diff)/2
