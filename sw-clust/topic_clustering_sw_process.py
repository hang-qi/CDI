import glob
import logging
from model import topic_model
from model import document
from preprocessing import cleansing, vocabulary
import datetime


def read_triplet_file(triplet_filename, use_ocr=False):
    ocr_file = None
    if use_ocr:
        ocr_file = triplet_filename.replace('triplet_files_small/', 'ocr/ocr_result/').replace('.txt', '.ocr').lower()
    np1_words = []
    vp_words = []
    np2_words = []
    with open(triplet_filename, 'r') as f:
        for line in f:
            if(line[0] != '<'):
                line = (line[:-2]).lower()
                triplets = line.split('|')
                np1_words.extend(cleansing.clean(triplets[0].split()))
                vp_words.extend(cleansing.clean(triplets[1].split()))
                np2_words.extend(cleansing.clean(triplets[2].split()))
    ocr_words = []
    with open(ocr_file, 'r') as f:
        for line in f:
            if(line[0] != '<'):
                line = (line[:-2]).lower()
                ocr_words.extend(cleansing.clean(line.split()))

    timestamp = datetime.datetime.strptime((triplet_filename.split('_')[0]).split('.')[0], '%Y%m%d%H%M%S')

    return document.OrignalDocument(triplet_filename[:-4].split('_')[1], timestamp, np1_words, vp_words, np2_words, ocr_words)


def main():
    logging.basicConfig(level=logging.DEBUG)
    input_triplet_files = glob.glob('triplet_files_small/2008*.txt')
    input_triplet_files.sort()
    logging.debug('Files {0}'.format(len(input_triplet_files)))

    # Generate initial corpus
    initial_corpus = topic_model._Corpus()

    # Read in the triplets files, including the triplets and the time of the story
    for triplet_file in input_triplet_files:
        initial_corpus.add_document(read_files(triplet_file, use_ocr=True))

    # Train topic model
    model = TopicMode()
    model.feed(initial_corpus)

        # waiting long long time (multiple level sw)...

    # current_tree = model.topic_tree


if __name__ == '__main__':
    main()
