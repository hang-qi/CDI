# Match the topic labels obtained from Vanderbilt to the tpt files
# The result is the original tpt file with topic labels added, file name: '*.tpt.topic'

import sys
sys.path.append('..')
import re
import glob
import codecs
import logging

# The path should contain tpt files and the corresponding topic label files
# Note: the command to get the topic label files: 
#       for FIL in `ls -1 *CNN*` ; do [path]cc-Vandy $FIL ; done &> [path]*_topic_label.txt
def align_topic_label(filepath):
    filename = filepath + '*.tpt'
    files = glob.glob(filename)
    files.sort()

    for tpt_file in files:
        label_file = tpt_file.split('.')[0] + '_topic_label.txt'
        output_file = tpt_file + '.topic'
        output_f = open(output_file, 'w')

        ## First read in the labels
        start_time = []
        end_time = []
        topic = []
        with open(label_file, 'r') as f:
            for line in f:
                line = line[:-1]
                components = line.split('|')
                start_time.append(components[0])
                end_time.append(components[1])
                topic.append(components[4])

        topic_num = len(topic)

        ## Then add the labels in the tpt files
        
        topic_pointer = 0;
        while (topic_pointer < topic_num and not topic_check(topic[topic_pointer])):
            topic_pointer += 1

        topic_end = False
        
        with open(tpt_file, 'r') as f:
            for line in f:
                line = line[:-1]
                components = line.split('|')
                if len(components) >= 4 and not topic_end:
                    if components[2] == 'SEG':
                        if topic_check(topic[topic_pointer]):
                            if 'Type=Story' in components[3]:
                                line += ', ' + topic[topic_pointer]
                                topic_pointer += 1
                                if topic_pointer >= topic_num:
                                    topic_end = True
                        else:
                            if '(Commercial:' in topic[topic_pointer]:
                                if 'Type=Commercial' in components[3]:
                                    topic_pointer += 1
                                    if topic_pointer >= topic_num:
                                        topic_end = True
                            else:
                                # Search until commercial
                                while (topic_pointer < topic_num and '(Commercial:' not in topic[topic_pointer]):
                                    topic_pointer += 1
                                if 'Type=Commercial' in components[3]:
                                    topic_pointer += 1
                                    if topic_pointer >= topic_num:
                                        topic_end = True
                                else:
                                    if topic_pointer >= topic_num:
                                        topic_end = True

                output_f.write(line + '\n')
        output_f.close()


def topic_check(topic):
    stop_words = ['Topic=Introduction', 'Upcoming Items', '(Commercial:', '360 Bulletin', '360 Dispatch', 'Beat 360', 'Topic=The Shot', 'Topic=Good Night']
    for stop_word in stop_words:
        if stop_word in topic:
            return False
    return True


def main():
    align_topic_label('New Data/*/')


if __name__ == '__main__':
    main()