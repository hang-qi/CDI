# This script eliminates the stop words.

import sys
import codecs
import glob

import cleansing


CONTENT_LINE_TAG = ['cc0', 'ccO', 'cc1', 'tr0', 'tr1']


def filter_story(filename):
    filtered_words = []

    # read in story
    f = codecs.open(filename, 'r', encoding='ISO-8859-1')
    for line in f:
        line = line.lower()

        # only split and filter content lines
        # TAG|timestamp|conent
        parts = line.split('|')
        if (parts[0] in CONTENT_LINE_TAG):
            word_list = parts[-1].split(' ')
            filtered_words.extend(cleansing.remove_stopwords(word_list))
    f.close()

    # write the cleaned story to disk
    filterd_story = ' '.join(filtered_words)
    f = open(filename + '.txt', 'w')
    f.write(filterd_story)
    f.close()


def main():
    # read in stopwords
    segmented_files = glob.glob(sys.argv[1])  # Interprete the wildcards.
    for storyfile in segmented_files:
        filter_story(storyfile)
    return 0


if __name__ == '__main__':
    main()
