import sys
import re
import datetime
sys.path.append('..')
from preprocessing import cleansing


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

    def set_name(self, name1, name2):
        self.story_name = name1 + '|' + name2

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
        self.line_list.extend(cleansing.clean(line.split()))

    def add_ocr_line(self, line):
        self.ocr.extend(line)
