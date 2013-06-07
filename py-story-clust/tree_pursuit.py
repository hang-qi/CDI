# Pursuit a topic tree.
import logging
import glob
import copy

from storyclustering import storyclustering
from preprocessing import cleansing
from vocabulary import vocabulary
from model.topic_tree import TopicTree
from model.corpus import Corpus, CorpusStatistics, Document, DocumentStatistics, Distribution


def propose_next(current_tree, corpus):
    """Purpose new trees by pairwise combination."""
    num_main_branches = len(current_tree.nodes)
    canididates = []
    # Here we perform a exhaust search to propose all possible combinations.
    # Heuristics can be added to skip certain candidates.
    for i in range(0, num_main_branches):
        #logging.debug('Proposing {0}...'.format(i))
        for j in range(0, num_main_branches):
            if (i < j):
                # Combine node x and y
                new_tree = copy.deepcopy(current_tree)
                new_tree.combine_branch(i, j)
                assert(new_tree is not current_tree)

                affected = copy.deepcopy(current_tree.branch_terminals[i])
                affected.extend(current_tree.branch_terminals[j])

                candidate_lh_affected = new_tree.likelihood(
                    corpus, subset=affected)

                canididates.append(((i, j), candidate_lh_affected, affected))
    return canididates


def greedy_pursuit(initial_tree, corpus):
    best_candidate = initial_tree
    #max_posterior_gain = 1
    min_likelihood_change = 0

    #while (max_posterior_gain > 0):
    while(abs(min_likelihood_change) < 200):
        current_tree = best_candidate
        #current_prior = calculate_prior(len(current_tree.nodes))
        logging.debug('Tree: {0}'.format(current_tree.nodes))

        # Generate candidates
        logging.info('Generating candidates...')
        new_candidates = propose_next(current_tree, corpus)
        logging.info('# of candidates: {0}'.format(len(new_candidates)))

        # Prior for all candidates are same, since
        #candidate_prior = calculate_prior(len(current_tree.nodes)-1)

        logging.info('Evaluating candidates...')
        min_likelihood_change = 220
        for (combined_branches, candidate_lh_affected, affected_terminals) in new_candidates:
            # Calculate likelihood reduction.
            current_lh_affected = current_tree.likelihood(corpus, subset=affected_terminals)
            likelihood_change = abs(candidate_lh_affected - current_lh_affected)

            #if posterior_gain > max_posterior_gain and posterior_gain != 0:
            if likelihood_change < min_likelihood_change:
                logging.debug(10*'-')
                logging.debug('Likelihood Values: {0} vs. {1}'.format(
                    candidate_lh_affected, current_lh_affected))
                logging.debug('Likelihood Change: {0}'.format(likelihood_change))
                logging.debug('Affected files:')
                for terminal_id in affected_terminals:
                    logging.debug('\t{0} : {1}'.format(
                        terminal_id, corpus.get_document_name(terminal_id)))

                best_candidate = copy.deepcopy(current_tree)
                best_candidate.combine_branch(
                    combined_branches[0], combined_branches[1])
                min_likelihood_change = likelihood_change
        #logging.debug('Posterior Gain: {0}'.format(max_posterior_gain))

    return current_tree


def pursuit_tree(input_triplet_files, co_mat_file=None, diffuse=False, use_ocr=False):
    logging.info('Building vocabulary...')
    corpus = Corpus(initialize_corpus_statistics(input_triplet_files))

    # calculate histogram
    logging.info('Calculating histograms of each story...')
    for triplet_file in input_triplet_files:
        (doc, doc_stat) = read_triplet_document(triplet_file, corpus.statistics.vocabularies, use_ocr=use_ocr)
        corpus.add_document(doc, doc_stat)

    # initial tree
    logging.info('Calculating Initial Tree...')
    initial_tree = TopicTree(corpus.statistics)

    # start pursuit
    logging.info('Pursuing a optimum tree...')
    optimum_tree = greedy_pursuit(initial_tree, corpus)
    return optimum_tree


def initialize_corpus_statistics(triplets_files):
    np1_vocab = build_vocabulary(triplets_files, word_type='NP1')
    vp_vocab = build_vocabulary(triplets_files, word_type='VP')
    np2_vocab = build_vocabulary(triplets_files, word_type='NP2')
    return CorpusStatistics(np1_vocab, vp_vocab, np2_vocab)


def read_triplet_document(triplet_file, vocabularies, use_ocr=False):
    ocr_file = None
    if use_ocr:
        ocr_file = triplet_file.replace('triplet_files_small/', 'ocr/ocr_result/').replace('.txt', '.ocr').lower()

    (hist_np1, np1_words, ocr_words) = storyclustering.learn_story_histogram(
        triplet_file, vocabularies[0], word_type='NP1', ocr_file=ocr_file)
    (hist_vp, vp_words, ocr_words) = storyclustering.learn_story_histogram(
        triplet_file, vocabularies[1], word_type='VP', ocr_file=ocr_file)
    (hist_np2, np2_words, ocr_words) = storyclustering.learn_story_histogram(
        triplet_file, vocabularies[2], word_type='NP2', ocr_file=ocr_file)

    distribution_np1 = Distribution(hist_np1, len(np1_words))
    distribution_vp = Distribution(hist_vp, len(vp_words))
    distribution_np2 = Distribution(hist_np2, len(np2_words))
    distributions = (distribution_np1, distribution_vp, distribution_np2)
    document_stat = DocumentStatistics(distributions, ocr_words)

    doc_name = triplet_file.split('_')[-1]
    document = Document(doc_name, np1_words, vp_words, np2_words, ocr_words)
    return (document, document_stat)


def build_vocabulary(input_triplet_files, word_type='ALL'):
    vocab = vocabulary.Vocabulary()
    for triplet_file in input_triplet_files:
        with open(triplet_file, 'r') as f:
            for line in f:
                if(line[0] != '<'):
                    line = (line[:-2]).lower()
                    triplets = line.split('|')
                    words = []
                    if (word_type == 'NP1' or word_type == 'ALL'):
                        words.extend(cleansing.clean(triplets[0].split()))
                    if (word_type == 'VP' or word_type == 'ALL'):
                        words.extend(cleansing.clean(triplets[1].split()))
                    if (word_type == 'NP2' or word_type == 'ALL'):
                        words.extend(cleansing.clean(triplets[2].split()))

                    for w in words:
                        vocab.add(w)
    logging.info('Vocabulary: {0}, {1}.'.format(word_type, vocab.size()))
    return vocab


def main():
    logging.basicConfig(level=logging.DEBUG)

    # input data
    input_triplet_files = glob.glob('triplet_files_small/2008*.txt')
    #input_triplet_files = glob.glob('triplet_files/[13]*.txt')
    input_triplet_files.sort()
    logging.debug('Files {0}'.format(len(input_triplet_files)))

    # pursuit tree
    optimum_tree = pursuit_tree(input_triplet_files, use_ocr=True)  # 'mat/np1_co_mat')

    labels_long = [filename.split('/')[-1][:-4] for filename in input_triplet_files]
    labels_short = [filename.split('_')[-1][:-4] for filename in input_triplet_files]

    optimum_tree.print_hiearchy(labels=labels_long, synthesize_title=True)

    with open('visualize/data.json', 'w') as fw:
        optimum_tree.print_hiearchy_json(fw, labels=labels_short, synthesize_title=False)
    return


if __name__ == '__main__':
    main()
