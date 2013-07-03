# Probability
import numpy


class Probability(object):
    def __init__(self, nrow, ncol):
        self.row_num = nrow
        self.col_num = ncol
        self.prob = numpy.empty((nrow, ncol))

    def set_value(self, row, col, value):
        if row in range(0, self.row_num) and col in range(0, self.col_num):
            self.prob[row, col] = value
        else:
            print('Set Probability Out of Index')

    def check_probability(self, value):
        if sum(sum(self.prob)) == value:
            return True
        else:
            return False

    def get_value(self, row, col):
        if row in range(0, self.row_num) and col in range(0, self.col_num):
            return self.prob[row, col]
        else:
            print('Set Probability Out of Index')
            return -1
