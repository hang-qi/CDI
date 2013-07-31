import glob
import logging
from model import topic_model
from preprocessing import readingfiles


def main():
    logging.basicConfig(level=logging.DEBUG)
    input_triplet_files = glob.glob('data/triplet_files_new_test_set/2008*.txt')
    input_triplet_files.sort()
    logging.debug('Files {0}'.format(len(input_triplet_files)))

    # Read in the triplets files, including the triplets and the time of the story
    original_documents = []
    for triplet_file in input_triplet_files:
        original_documents.append(readingfiles.read_triplet_file(triplet_file, use_ocr=True))

    # Train topic model
    model = topic_model.TopicModel(classifier_model_filename='preprocessing/model_segmenter.txt')
    model.feed(original_documents)

    # current_tree = model.topic_tree


if __name__ == '__main__':
    main()
