import glob
import logging
from model import topic_model
from model import document
from preprocessing import cleansing
import datetime


def read_triplet_file(triplet_filename, use_ocr=False):
    ocr_file = None
    if use_ocr:
        ocr_file = triplet_filename.replace('data/triplet_files_new_test_set/', 'data/ocr_result/').replace('.txt', '.ocr').lower()
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

    timestamp = datetime.datetime.strptime(((triplet_filename.split('/')[-1]).split('_')[0]).split('.')[0], '%Y%m%d%H%M%S')
    filename = triplet_filename.split('/')[-1][:-4].split('_')[1]
    return document.OrignalDocument(filename, timestamp, np1_words, vp_words, np2_words, ocr_words)


def main():
    logging.basicConfig(level=logging.DEBUG)
    input_triplet_files = glob.glob('data/triplet_files_new_test_set/2008*.txt')
    input_triplet_files.sort()
    logging.debug('Files {0}'.format(len(input_triplet_files)))

    # Read in the triplets files, including the triplets and the time of the story
    original_documents = []
    for triplet_file in input_triplet_files:
        original_documents.append(read_triplet_file(triplet_file, use_ocr=True))

    # Train topic model
    model = topic_model.TopicModel(classifier_model_filename='preprocessing/model_segmenter.txt')
    model.feed(original_documents)

    # current_tree = model.topic_tree


if __name__ == '__main__':
    main()
