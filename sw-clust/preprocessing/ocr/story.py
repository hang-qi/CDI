import sys
import re
import datetime
sys.path.append('..')
import cleansing
import difflib


class Story(object):
    """A Story contains the story name, start and end time, and a line list"""
    def __init__(self):
        super(Story, self).__init__()
        self.story_name = None
        self.start_time_string = None
        self.end_time_string = None
        self.start_time_minute = 0
        self.start_time_second = 0
        self.end_time_minute = 0
        self.end_time_second = 0
        self.line_list = []
        self.ocr = []

    def set_name(self, name):
        self.story_name = name

    def set_start_time(self, starttime):
        self.start_time_string = starttime   	
        reprog = re.compile(r"""\d\d\d\d\d\d\d\d\d\d(\d\d)(\d\d).+""", re.I | re.X)
        m = reprog.match(starttime)
        g = m.groups()
        self.start_time_minute = int(g[0])
        self.start_time_second = int(g[1])      

    def set_end_time(self, endtime):
        self.end_time_string = endtime
        reprog = re.compile(r"""\d\d\d\d\d\d\d\d\d\d(\d\d)(\d\d).+""", re.I | re.X)
        m = reprog.match(endtime)
        g = m.groups()
        self.end_time_minute = int(g[0])
        self.end_time_second = int(g[1])

    def add_line(self, line):
        words = cleansing.clean(line.split())
        for w in words:
            self.line_list.append(w)

    def add_ocr_line(self, line):
        similar_ratio = 0
        if line not in self.ocr:
            for l in self.ocr:
                a = l.split()
                b = line.split()
                similarity = difflib.SequenceMatcher(None, a, b)
                similar_ratio_tmp = similarity.ratio()
                if similar_ratio_tmp > similar_ratio:
                    similar_ratio = similar_ratio_tmp
            if similar_ratio < 0.5:
                line.replace('III','IN')
                self.ocr.append(line)
