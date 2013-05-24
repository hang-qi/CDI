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


def build_sub_contextual_matrix_and_save(
        whole_vocab, story_files, vocab_filename, matrix_filename):
    """Build a contextual distribution matrix on a subset of corpus."""

    start_time = time.time()

    stories = []
    words = []
    for story_file in story_files:
        story_words = read_story(story_file)
        words.extend(story_words)
        stories.append(story_words)

    sub_matrix_vocab = vocabulary.Vocabulary()
    sub_matrix_vocab.build_by_list(list(set(words)))

    logging.debug('Unique words in this batch: {0}.'.format(sub_matrix_vocab.size()))
    logging.debug('Calculating frequencies...')

    sub_contextual_mat = np.zeros((sub_matrix_vocab.size(), whole_vocab.size()))

    for i in range(0, len(stories)):
        story_words = stories[i]

        # count word frequencies in the story
        story_word_freq = {}
        for w in story_words:
            if w in story_word_freq:
                story_word_freq[w] = story_word_freq[w] + 1
            else:
                story_word_freq[w] = 1

        frequencies = [(u, v, story_word_freq[u]*story_word_freq[v])
            for u in story_word_freq.keys() for v in story_word_freq.keys()]

        # fill in the contextual distribution matrix
        for (u, v, frequency) in frequencies:
            try:
                u_id = sub_matrix_vocab.get_word_index(u)
                v_id = whole_vocab.get_word_index(v)
                if u == v:
                    sub_contextual_mat[u_id, v_id] += math.sqrt(frequency)
                else:
                    sub_contextual_mat[u_id, v_id] += frequency
            except ValueError:
                continue

    # Here we do not normalize the sub contextual matrix.
    # This will be normalized when build the co-occurrence matrix of interest.
    # See: calculate_cooccur_matrix_by_submatrices().

    # save sub matrices and vocabularies.
    sub_matrix_vocab.save(vocab_filename)
    save_matrix(matrix_filename, sub_contextual_mat)

    end_time = time.time()
    logging.debug("Time: %g seconds" % (end_time - start_time))

    return sub_contextual_mat


def calculate_cooccur_mat_by_submatrices_and_save(vocab_file_of_interest, full_vocab_size, files):
    # Load Vocabulary of interest
    vocab_of_interest = vocabulary.Vocabulary()
    vocab_of_interest.load(vocab_file_of_interest)

    logging.debug('Total # of words: {0}.'.format(vocab_of_interest.size()))

    # Build contextual distribution matrix for NP.
    contextual_mat = np.zeros((vocab_of_interest.size(), full_vocab_size))

    num_it = 0
    for (voc_filename, mat_filename) in files:
        num_it += 1

        # First read the sub vocabulary.
        sub_matrix_vocab = Vocabulary()
        sub_matrix_vocab.load(voc_filename)

        # Only load sub matrix if the matrix has the distribution we want.
        has_target_word = False
        target_words_rows = []
        for i in range(0, vocab_of_interest.size()):
            if sub_matrix_vocab.contain(words[i]):
                # get the row id of the interested word in sub matrix.
                row_id = sub_matrix_vocab.get_word_index(words[i])
                target_words_rows.append(row_id)
                has_target_word = True
            else:
                # if cannot find the word of interest in the vocabulary,
                # mark as -1.
                target_words_rows.append(-1)

        if has_target_word:
            sub_matrix = np.load(mat_filename)
            for i in range(0, vocab_of_interest.size()):
                row_id = target_words_rows[i]
                if row_id != -1:
                    contextual_mat[i] += sub_matrix[row_id]

    # remove the words with no distribution information.
    row_sums = contextual_mat.sum(axis=1)
    rows_to_delete = []
    for i in range(0, vocab_of_interest.size()):
        if row_sums[i] == 0:
            rows_to_delete.append(i)
            logging.warning('No contextual information for: {0}'.format(words[i]))
    logging.warning('# of words deleted: {0}'.format(len(rows_to_delete)))

    # delete corresponding rows from matrix.
    contextual_mat = np.delete(contextual_mat, rows_to_delete, 0)
    row_sums = np.delete(row_sums, rows_to_delete, 0)

    # build new vocabulary after deletion.
    vocab_after_delete = vocabulary.Vocabulary()
    for w in vocab_of_interest.word_list:
        if vocab_of_interest.get_word_index(w) not in rows_to_delete:
            vocab_after_delete.add(w)

    # normalize.
    contextual_mat = contextual_mat / row_sums.reshape(-1, 1)

    # Build the co-occurrence matrix by contextual matrix.
    co_mat = calculate_cooccur_matrix(contextual_mat)
    logging.debug(co_mat)

    # Save matrix, vocabulary, and deleted vocabulary.
    co_mat_filename = vocab_file_of_interest.replace('.voc', '_co_mat.npy')
    vocab_filename = vocab_file_of_interest.replace('.voc', '_co_mat.voc')
    save_matrix(co_mat_filename, co_mat)
    vocab_after_delete.save(vocab_filename)

    return co_mat


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


def save_matrix(filename, matrix):
    np.save(filename, matrix)
    return


def read_story(filename):
    with codecs.open(filename, 'r', encoding='ISO-8859-1') as f:
        content = f.read()
    words = content.split()
    return words
