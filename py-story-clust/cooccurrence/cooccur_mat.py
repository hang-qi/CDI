# Learn co-occurrence matrix from data
import codecs
import logging
import math
import time
import numpy as np

from vocabulary import vocabulary


def learn_matrix(story_files):
    """Learn a word co-occurrence matrix from corpus."""

    logging.debug("Calculating matrix from {0} files".format(len(story_files)))
    # build vocabulary
    vocab = build_vocabulary(story_files)
    vocab.save('vocabulary.voc')

    # build matrix and fill in
    matrix = build_cooccur_matrix(vocab, story_files)
    save_matrix('co_mat.npy', matrix)
    return matrix


def build_vocabulary(story_files):
    """Build a vocabulary from a set of given tpt files."""
    voc = vocabulary.Vocabulary()

    for story_file in story_files:
        words = read_story(story_file)
        for w in words:
            voc.add(w)

    logging.debug('Vocabulary obtained: {0} words.'.format(voc.size()))
    logging.debug('Print 15 words:')
    for i in range(0, 15):
        logging.debug('{0}: {1}'.format(i, voc.get_word(i)))
    return voc


def build_cooccur_matrix(vocab, story_files):
    """Build co-occurrence matrix."""
    contextual_mat = calcuate_contextual_mat(vocab, story_files)
    cooccur_mat = calculate_cooccur_matrix(contextual_mat)
    return cooccur_mat


def calcuate_contextual_mat(vocab, story_files):
    """Calculate contextual distribution matrix."""
    # TODO: fill in co-occurrence matrix
    num_words = vocab.size()
    contextual_mat = np.zeros((num_words, num_words))

    for story_file in story_files:
        words = read_story(story_file)
        wordset = set(words)

        # frequencies = [ (u_id, v_id, p_u(v))]
        frequencies = [(vocab.get_word_index(u), vocab.get_word_index(v),
            words.count(u)*words.count(v)) for u in wordset for v in wordset]

        for (u_id, v_id, time_frequency) in frequencies:
            if u_id == v_id:
                contextual_mat[u_id, v_id] += math.sqrt(time_frequency)
            else:
                contextual_mat[u_id, v_id] += time_frequency

    # normalize so that each row will sum to one.
    row_sums = contextual_mat.sum(axis=1)
    contextual_mat = contextual_mat / row_sums.reshape(-1, 1)

    logging.debug('Print 15*15 contextual distribution:')
    logging.debug(contextual_mat[0:15, 0:15])
    logging.debug(contextual_mat[np.ix_([1, 3, 5], [1, 3, 5])])

    return contextual_mat


def build_sub_contextual_matrix_and_save(whole_vocab, story_files, batch_id):
    start_time = time.time()

    stories = []
    words = []
    for story_file in story_files:
        story_words = read_story(story_file)
        words.extend(story_words)
        stories.append(story_words)

    unique_words = list(set(words))
    word_dict = {}      # maps: word -> idx
    for i in range(0, len(unique_words)):
        word_dict[unique_words[i]] = i

    logging.debug('Unique words in this batch: {0}.'.format(len(unique_words)))
    logging.debug('Calculating frequencies...')

    sub_contextual_mat = np.zeros((len(unique_words), whole_vocab.size()))

    for i in range(0, len(stories)):
        #logging.debug('File {0} : {1}.'.format(i, story_files[i]))
        story_words = stories[i]

        # count word frequencies in the story
        story_dict = {}
        for w in story_words:
            if w in story_dict:
                story_dict[w] = story_dict[w] + 1
            else:
                story_dict[w] = 1

        frequencies = [(u, v, story_dict[u]*story_dict[v])
            for u in story_dict.keys() for v in story_dict.keys()]

        for (u, v, time_frequency) in frequencies:
            u_id = word_dict[u]
            v_id = whole_vocab.get_word_index(v)
            if v_id == -1:
                continue
            if u == v:
                sub_contextual_mat[u_id, v_id] += math.sqrt(time_frequency)
            else:
                sub_contextual_mat[u_id, v_id] += time_frequency

    # do not normalize sub contextual matrix.

    # save sub matrices and vocabularies.
    save_word_list('../data/sub_matrix_{0}.voc'.format(batch_id), unique_words)
    save_matrix('../data/sub_matrix_{0}.npy'.format(batch_id), sub_contextual_mat)

    end_time = time.time()
    logging.debug("Time: %g seconds" % (end_time - start_time))

    return sub_contextual_mat


def calculate_cooccur_matrix(contextual_mat):
    """Calculate co-occurrence matrix based on contextual distribution matrix."""
    num_words = contextual_mat.shape[0]
    cooccur_mat = np.zeros((num_words, num_words))

    # only calculate the upper triangle matrix.
    for u in range(0, num_words):
        for v in range(u, num_words):
            sqrt_sum = ((contextual_mat[u] * contextual_mat[v])**0.5).sum()
            #logging.debug('sqrt = {0}'.format(sqrt_sum))
            power = 0
            if sqrt_sum >= 1:
                if math.fabs(sqrt_sum - 1.0) > 0.00001:
                    logging.warning('sqrt_sum >= 1 is {0}'.format(sqrt_sum))
                power = 0
            else:
                power = math.acos(sqrt_sum) ** 2
            cooccur_mat[u, v] = math.exp(-1 * power)

    # recover the whole matrix.
    cooccur_mat = cooccur_mat + np.tril(cooccur_mat.T, -1)

    logging.debug('Print 15*15 similarity matrix:')
    logging.debug(cooccur_mat[0:15, 0:15])
    return cooccur_mat


def save_word_list(filename, words):
    with codecs.open(filename, 'w', encoding='ISO-8859-1') as f:
        for w in words:
            f.writelines(w + '\n')
    return


def save_matrix(filename, matrix):
    np.save(filename, matrix)
    return


def read_story(filename):
    with codecs.open(filename, 'r', encoding='ISO-8859-1') as f:
        content = f.read()
    words = content.split()
    return words
