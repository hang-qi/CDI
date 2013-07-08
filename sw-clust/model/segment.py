# Defines the segment


class Segment(object):
    def __init__(self, lableing=None):
        # the boundary is the No. of the left sentence, start from 0
        self.seg_boundary = []

    def add_boundary(self, boundary):
        self.seg_boundary.append(boundary)
