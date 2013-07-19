# Probability
import mpmath


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
