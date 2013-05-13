# This script eliminates the stop words.

import sys
import codecs
import glob

import cleansing


CONTENT_LINE_TAG = ['cc0', 'cco', 'cc1', 'tr0', 'tr1']


def filter_story(filename):
    filtered_words = []

    # read in story
    with codecs.open(filename, 'r', encoding='ISO-8859-1') as f:
        for line in f:
            line = line.lower()

            # only split and filter content lines
            # TAG|timestamp|conent
            parts = line.split('|')
            if (parts[0] in CONTENT_LINE_TAG):
                word_list = parts[-1].split(' ')
                word_list = cleansing.clean(word_list)
                filtered_words.extend(word_list)

    # write the cleaned story to disk
    filterd_story = ' '.join(filtered_words)
    with codecs.open(filename + '.txt', 'w', encoding='ISO-8859-1') as f:
        f.write(filterd_story)


def main():
    # read in stopwords
    segmented_files = glob.glob(sys.argv[1])
    for storyfile in segmented_files:
        filter_story(storyfile)
    return 0


if __name__ == '__main__':
    main()
