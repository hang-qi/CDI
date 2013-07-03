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
            print('Set Probability Out of Index {0}, {1}'.format(row, col))

    def check_probability(self, value):
        if sum(sum(self.prob)) == value:
            return True
        else:
            print('Probability Sum: {0}'.format(sum(sum(self.prob))))
            return False

    def get_value(self, row, col):
        if row in range(0, self.row_num) and col in range(0, self.col_num):
            return self.prob[row, col]
        else:
            print('Get Probability Out of Index {0}, {1}'.format(row, col))
            return -1

    def print_prob(self):
        for i in range(self.row_num):
            for j in range(self.col_num):
                print(self.get_value(i, j))
