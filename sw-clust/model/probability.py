# Probability
import numpy as np
import mpmath


class Distribution(object):
    """A 1D histogram (normalized to 1)."""
    def __init__(self, histogram=None):
        if histogram is not None:
            self.set_histogram(histogram)
        else:
            self._hist = None
            self._denominator = 1
            self._length = 0

    def set_histogram(self, histogram):
        self._hist = histogram
        self._denominator = sum(histogram)
        self._length = len(histogram)
        if self._denominator != 1 and self._denominator != 0:
            self._hist /= self._denominator

    def __contains__(self, word_id):
        return (0 <= word_id < self._length)

    def __getitem__(self, word_id):
        if self._hist is not None:
            return self._hist[word_id]
        else:
            raise ValueError('The distribution is empty.')

    def __add__(self, other):
        # Recover histogram and add.
        if self._hist is not None:
            new_hist = self._hist * self._denominator + other._hist * other._denominator
            return Distribution(new_hist)
        else:
            return other

    def __radd__(self, other):
        # The 'add' operation among distribution if symmetric.
        return self.__add__(other)

    def __iadd__(self, other):
        return self.__add__(other)

    def kl_divergence(self, other):
        p = self._hist
        q = other._hist
        assert(self._length == other._length)
        #kl_array = [p[i]*(mpmath.log(p[i] + 1e-100) - mpmath.log(q[i] + 1e-100)) for i in range(0, self._length)]
        kl_array = p*np.log((p + 1e-100)/(q + 1e-100))
        kl_value = sum(kl_array)
        return kl_value

    def tv_norm(self, other):
        assert(self._length == other._length)
        diff = np.absolute(self._hist - other._hist)
        return mpmath.mpf(np.sum(diff))/2.0

    def combine(self, other):
        self = self.__add__(other)

    def get_top_word_ids(self, num_words):
        """Synthesize a set of words from the distribution."""
        indexes = np.argsort(self._hist)
        top_words_id = indexes[::-1][0:min(num_words, len(self._hist))]
        filtered_id = [wid for wid in top_words_id if self._hist[wid] > 0]
        return filtered_id


class Probability(object):
    def __init__(self, nrow, ncol):
        self._row_num = nrow
        self._col_num = ncol
        self.prob = mpmath.matrix(nrow, ncol)  # numpy.empty((nrow, ncol))

    def check_probability(self, value):
        if sum(sum(self.prob)) == value:
            return True
        else:
            print('Probability Sum: {0}'.format(sum(sum(self.prob))))
            return False

    def normalize(self, row):
        dist_sum = sum(self.prob[row, :])
        for col in range(0, self._col_num):
            self.prob[row, col] /= dist_sum

    def __getitem__(self, index):
        if type(index) is int:
            [row, col] = [0, index]
        else:
            [row, col] = index
        assert(col >= 0 and col < self._col_num)
        assert(row >= 0 and row < self._row_num)
        return self.prob[row, col]

    def __setitem__(self, index, value):
        if type(index) is int:
            [row, col] = [0, index]
        else:
            [row, col] = index
        assert(row >= 0 and row < self._row_num)
        assert(col >= 0 and col < self._col_num)
        self.prob[row, col] = value

    def set_value(self, row, col, value):
        assert(row >= 0 and row < self._row_num)
        assert(col >= 0 and col < self._col_num)
        self.prob[row, col] = value

    def get_value(self, row, col):
        assert(row >= 0 and row < self._row_num)
        assert(col >= 0 and col < self._col_num)
        return self.prob[row, col]

    def print_prob(self):
        for i in range(self._row_num):
            for j in range(self._col_num):
                print(self.get_value(i, j))
