import sys
import getopt
import string
import codecs
import re
import datetime
import calendar
from html.parser import HTMLParser

# my scripts
import timezone
monthNumberDict = dict((v,k) for k,v in enumerate(calendar.month_name))

class TranscriptHTMLParser(HTMLParser):
    # P elements we are interested in
    bodyAttr = ('class', 'cnnBodyText')
    HeadAttr = ('class', 'cnnTransStoryHead')  # Program title, like CNN NEWSROOM
    TopicAttr = ('class', 'cnnTransSubHead')   # Topics
    
    # enum values indicates the type of paragraph we are parsing
    PARAGRAPH_NORMAL = 0
    PARAGRAPH_BODY = 1
    PARAGRAPH_HEAD = 2
    PARAGRAPH_TOPIC = 3

    def __init__(self):
        super(TranscriptHTMLParser, self).__init__(self)
        self.paragraphStack = []

        self.head = []
        self.subHead = []
        self.paragraphs = []
        self.meta = []
        self.buffer = []


    def handle_starttag(self, tag, attrs):
        if (tag == "p"):
            if (TranscriptHTMLParser.bodyAttr in attrs):
                self.paragraphStack.append(TranscriptHTMLParser.PARAGRAPH_BODY)

            elif (TranscriptHTMLParser.HeadAttr in attrs):
                self.paragraphStack.append(TranscriptHTMLParser.PARAGRAPH_HEAD)

            elif (TranscriptHTMLParser.TopicAttr in attrs):
                self.paragraphStack.append(TranscriptHTMLParser.PARAGRAPH_TOPIC)

            else:
                self.paragraphStack.append(TranscriptHTMLParser.PARAGRAPH_NORMAL)
        if (tag == "br"):
            self.buffer.append('\n')


    def handle_endtag(self, tag):
        if (tag == "p"):
            last = len(self.paragraphStack) - 1
            if (self.paragraphStack[last] == TranscriptHTMLParser.PARAGRAPH_BODY):
                data = ''.join(self.buffer);
                if (len(data) < 500):
                    self.meta.append("(META) ")
                    self.meta.append(data + '\n')
                else:
                    #self.paragraphs.append("(DATA) ")
                    self.paragraphs.append(data + '\n')
            self.buffer = []
            self.paragraphStack.pop();


    def handle_data(self, data):
        if (len(self.paragraphStack) > 0):
            last = len(self.paragraphStack) - 1
            if (self.paragraphStack[last] == TranscriptHTMLParser.PARAGRAPH_BODY):
                # get rid of the empty lines
                if (data == ' '):
                    return
                # remove '\n' in HTML files
                self.buffer.append(data.replace('\n',''))
                self.buffer.append(' ')

            elif (self.paragraphStack[last] == TranscriptHTMLParser.PARAGRAPH_HEAD):
                self.head.append('(HEAD) '  + data.replace('\n','') + '\n')

            elif (self.paragraphStack[last] == TranscriptHTMLParser.PARAGRAPH_TOPIC):
                self.subHead.append('(SUBHEAD) ' + data.replace('\n','') + '\n')

    def get_meta(self):
        return ''.join(self.meta)

    def get_head(self):
        return ''.join(self.head)

    def get_subhead(self):
        return ''.join(self.subHead)

    def get_time(self):
        metadata = self.get_meta()
        parts = metadata.split("(META) ");
        reprog = re.compile(r"""^.*
            (January|February|March|April|May|July|June|August|September|October|November|December)\s
            (\d+),\s
            (20\d\d)\s*-\s*
            (\d+):(\d\d)\d*:?\d*\s*
            (\w*)\s*$""", re.I|re.X)

        et = timezone.Eastern;
        et_dt = datetime.datetime(2000, 1, 1, 0, 0, tzinfo=et);
        for part in parts:
            m = reprog.match(part)
            if m:
                g = m.groups()
                et_dt = et_dt.replace(month=monthNumberDict[g[0]]) # Month
                et_dt = et_dt.replace(day=int(g[1]))    # day
                et_dt = et_dt.replace(year=int(g[2]))   # year
                et_dt = et_dt.replace(hour=int(g[3]))   # hr
                et_dt = et_dt.replace(minute=int(g[4])) # minute
        return et_dt;

    def get_main_data(self):
        time = "(OBT) " + "{:%Y-%m-%d %H:%M America/New_York}".format(self.get_time());
        content = ''.join(self.paragraphs)
        content = content.replace('(COMMERCIAL BREAK)', '\n(COMMERCIAL BREAK)');        
        content = content.replace('\n\n', '\n');
        return self.get_head() + self.get_subhead() + time + content;

# In CNN transcripts are encoded as latin-1 (ISO-8859-1).
def convert(htmlFilename, charset='ISO-8859-1'):
    str_list = [];
    f = codecs.open(htmlFilename, encoding=charset)
    for line in f:    
        str_list.append(line)
    f.close()

    transcriptPage = ''.join(str_list)

    parser = TranscriptHTMLParser()
    parser.feed(transcriptPage)

    fo = open(htmlFilename.replace('.html','.rawtxt'), "w", encoding=charset)  # keep the same charset
    fo.write(parser.get_main_data())
    fo.close()

def main():
    filelist = sys.argv[1:]
    for filename in filelist:
        convert(filename)
        #convert('cnr.01.html')
    return

if __name__ == '__main__':
    main();