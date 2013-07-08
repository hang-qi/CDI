# Probability
import numpy


class Probability(object):
    def __init__(self, nrow, ncol):
        self.row_num = nrow
        self.col_num = ncol
        self.prob = numpy.empty((nrow, ncol))

    def set_value(self, row, col, value):
        assert(row >= 0 and row < self.row_num)
        assert(col >= 0 and col < self.col_num)
        self.prob[row, col] = value

    def check_probability(self, value):
        if sum(sum(self.prob)) == value:
            return True
        else:
            print('Probability Sum: {0}'.format(sum(sum(self.prob))))
            return False

    def get_value(self, row, col):
        assert(row >= 0 and row < self.row_num)
        assert(col >= 0 and col < self.col_num)
        return self.prob[row, col]

    def print_prob(self):
        for i in range(self.row_num):
            for j in range(self.col_num):
                print(self.get_value(i, j))
