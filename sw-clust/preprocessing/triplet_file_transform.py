# Read the original triplet files generated from the tpt files and transform them into
# the files each of which contains only the triplets of one story.
import glob
import sys
sys.path.append('..')
import logging


def read_original_triplet_file(filename, outputpath):
    #logging.debug('File: {0}'.format(filename))
    with open(filename, 'r') as f:
        triplet_lines = []
        for line in f:
            if line[0] == '<':
                #logging.debug('Line: {0}'.format(line))
                if line[1:6] == 'story':  # story: record the name of the current story
                    story_name_line = line
                    story_name = line.split('>')[-2].split('<')[0]
                    story_name = story_name.replace(' / ', '__')
                    continue
                if line[1:6] == 'start':  # start: recorf the start time of the current story
                    start_time_line = line
                    start_time = line.split('>')[-2].split('<')[0]
                    triplet_lines = []
                    continue
                if line[1:4] == 'end':  # end: output the story
                    output_filename = outputpath + filename.split('/')[-1].split('.')[0] + '&' + start_time + '&' + story_name + '.txt'
                    out_f = open(output_filename, 'w')
                    out_f.write(story_name_line)
                    out_f.write(start_time_line)
                    out_f.write(line)  # end time line
                    for triplet_line in triplet_lines:
                        out_f.write(triplet_line + '\n')
                    out_f.close()
                    logging.debug('Write File: {0}'.format(output_filename))
            else:
                if len(line) < 2:
                    continue
                #logging.debug('Line: {0}'.format(line))
                if len(line.split(';')) == 3:
                    line_comp = line.split()
                    #if len(line_comp[-1]) == 9:
                    #    if line_comp[-1] == '-Infinity':
                    #        line_comp = line_comp[:-1]
                    t_line = ''
                    for i, c in enumerate(line_comp):
                        c_split = c.split('/')
                        if len(c_split) > 1:
                            word_type = c_split[1].split(';')[0]
                            if word_type == 'NP' or word_type == 'VP':
                                t_line += c_split[0] + ' '
                            else:
                                continue
                            if i != len(line_comp)-1:
                                t_line += '| '
                        else:
                            t_line += c_split[0] + ' '
                    triplet_lines.append(t_line)
                    #logging.debug('Stored Line: {0}'.format(t_line))


def read_triplet_files(filepath=None):
    filepath = '../data/original_triplet_files_080819-081015/'
    filenames = filepath + '*.dat'
    files = glob.glob(filenames)
    files.sort()
    outputpath = '../data/transformed_triplet_files_080819-081015/'
    for triplet_file in files:
        read_original_triplet_file(triplet_file, outputpath)


def main():
    logging.basicConfig(level=logging.DEBUG)
    read_triplet_files()


if __name__ == '__main__':
    main()
