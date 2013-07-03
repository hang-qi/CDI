# Probability
import numpy


class Probability(object):
    def __init__(self, nrow, ncol):
        self.row_num = nrow
        self.col_num = ncol
        self.prob = numpy.empty((nrow, ncol))

    def set_value(self, row, col, value):
        self.prob[row, col] = value

    def check_probability(self, value):
        if sum(sum(self.prob)) == value:
            return True
        else:
            return False

    def get_value(self, row, col):
        return self.prob[row, col]
