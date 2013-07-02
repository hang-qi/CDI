# Defines the segment


class Segment(object):
    def __init__(self):
        self.seg_num = 0
        # the boundary is the No. of the left sentence, start from 0
        self.seg_boundary = []

    def add_boundary(self, boundary):
        self.seg_num += 1
        self.seg_boundary.append(boundary)

