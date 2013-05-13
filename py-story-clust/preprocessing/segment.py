# This script segment a set of tpt files

import codecs
import sys
import glob


class Segment:
    def __init__(self):
        self.lines = []

    def addLine(self, line):
        self.lines.append(line)


# Given a tpt file to segment, this function returns a list a segments.
def segment_transcript(filename):
    # list of segments
    segments = []
    currentSegment = Segment()
    with codecs.open(filename, mode='r', encoding='ISO-8859-1') as f:
        for line in f:
            #print(line[0:len('SegEnd')])
            if (line[0:len('SegEnd')] == 'SegEnd'):
                currentSegment.addLine(line)
                # SegEnd|20120903135615.550|Type=Commercial
                parts = line.split('|')
                if (parts[-1] != 'Type=Commercial'):
                    # Commercial segments shall be dropped.
                    segments.append(currentSegment)
                currentSegment = Segment()
            else:
                currentSegment.addLine(line)
    return segments


def save_segments(filename, segments):
    """Save segments into separated files.
    filenames look like /dataset/segmented/Y/Y-m/Y-m-d/<name>.seg#.seg
    This path is generated from orginal tpt files by replacing 'full' with
    'segmented' in the directory tree.
    """

    for index, segment in enumerate(segments):
        segfilename = '{0}.{1:02d}.seg'.format(
            filename.replace('full', 'segmented'), index)
        print('Write segments {0} to file {1}'.format(index, segfilename))

        with open(segfilename, 'w') as f:
            for line in segment.lines:
                f.write(line)


def main():
    transcriptfiles = glob.glob(sys.argv[1])
    num_segments = 0
    num_files = 0

    for filename in transcriptfiles:
        #print(filename)
        segments = segment_transcript(filename)
        save_segments(filename, segments)
        num_segments += len(segments)
        num_files += 1

    print('Done! {0} segments were extracted from {1} transcripts.'.format(
        num_segments, num_files))

if __name__ == '__main__':
    main()
